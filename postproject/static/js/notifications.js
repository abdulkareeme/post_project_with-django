/**
 * هذا الملف يتعامل مع منطق الواجهة الأمامية لإشعارات الوقت الفعلي.
 * يتصل بخادم WebSocket ويستمع للإشعارات الجديدة.
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM جاهز، جاري محاولة الاتصال بـ WebSocket.");

    // احصل على معرف المستخدم الحالي من عنصر HTML مخفي أو من سمة بيانات.
    // هذا ضروري لضمان أن المستخدم يتلقى إشعاراته الخاصة فقط.
    // مثال: <body data-user-id="{{ request.user.id }}">
    const currentUserId = document.body.dataset.userId; 

    if (!currentUserId) {
        console.error("معرف المستخدم غير موجود. لا يمكن إنشاء اتصال WebSocket للإشعارات.");
        // يمكنك هنا عرض رسالة للمستخدم أو إخفاء ميزات الإشعارات.
        return;
    }

    // بناء عنوان URL لـ WebSocket.
    // استخدم 'ws://' لـ HTTP و 'wss://' لـ HTTPS.
    // تأكد من أن عنوان URL يطابق مسار WebSocket الذي قمت بتكوينه في Django Channels.
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${protocol}${window.location.host}/ws/notifications/${currentUserId}/`;

    let notificationSocket = null;

    /**
     * وظيفة لإنشاء اتصال WebSocket.
     */
    function connectWebSocket() {
        notificationSocket = new WebSocket(wsUrl);

        notificationSocket.onopen = function(e) {
            console.log("تم الاتصال بـ WebSocket بنجاح!");
            // يمكنك إرسال رسالة للتحقق من الاتصال إذا لزم الأمر
            // notificationSocket.send(JSON.stringify({ 'message': 'Hello from client!' }));
        };

        notificationSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("تم استلام رسالة WebSocket:", data);

            // تحقق من نوع الإشعار (إعجاب، تعليق، إلخ)
            if (data.type === 'notification') {
                const message = data.message;
                const notificationType = data.notification_type; // 'like' أو 'comment'
                const postId = data.post_id;
                const commentId = data.comment_id; // إذا كان إشعار تعليق
                const likerUsername = data.liker_username; // إذا كان إشعار إعجاب
                const commenterUsername = data.commenter_username; // إذا كان إشعار تعليق

                // عرض الإشعار للمستخدم
                displayNotification(message, notificationType, postId, likerUsername, commenterUsername);

                // يمكنك تحديث عدد الإشعارات في الواجهة الأمامية هنا
                updateNotificationCount();
            }
        };

        notificationSocket.onclose = function(e) {
            console.log("تم إغلاق اتصال WebSocket. الرمز:", e.code, "السبب:", e.reason);
            // حاول إعادة الاتصال بعد فترة وجيزة إذا لم يكن الإغلاق طبيعياً (مثل إغلاق المتصفح)
            if (e.code !== 1000) { // 1000 هو رمز الإغلاق العادي
                console.log("إعادة الاتصال بـ WebSocket بعد 3 ثوانٍ...");
                setTimeout(connectWebSocket, 3000);
            }
        };

        notificationSocket.onerror = function(e) {
            console.error("خطأ WebSocket:", e);
            // يمكنك عرض رسالة خطأ للمستخدم
        };
    }

    /**
     * وظيفة لعرض الإشعار في الواجهة الأمامية.
     * يمكنك تخصيص هذه الوظيفة لعرض الإشعارات بالطريقة التي تفضلها (مثل نافذة منبثقة، شريط علوي، إلخ).
     * @param {string} message - نص الإشعار.
     * @param {string} type - نوع الإشعار ('like' أو 'comment').
     * @param {number} postId - معرف المنشور المرتبط بالإشعار.
     * @param {string} likerUsername - اسم المستخدم الذي قام بالإعجاب (إذا كان إعجاب).
     * @param {string} commenterUsername - اسم المستخدم الذي قام بالتعليق (إذا كان تعليق).
     */
    function displayNotification(message, type, postId, likerUsername, commenterUsername) {
        // مثال بسيط: عرض الإشعار كـ "toast" أو "snackbar"
        const notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            console.warn("لم يتم العثور على عنصر 'notification-container'. يرجى إضافته إلى HTML الخاص بك.");
            alert(`إشعار جديد: ${message}`); // fallback
            return;
        }

        const notificationElement = document.createElement('div');
        notificationElement.className = 'bg-blue-500 text-white p-3 rounded-lg shadow-lg mb-2 animate-fade-in-down';
        notificationElement.innerHTML = `
            <p class="font-bold">إشعار جديد!</p>
            <p>${message}</p>
            <a href="/posts/${postId}/" class="text-blue-200 hover:underline">عرض المنشور</a>
        `;

        // إضافة الإشعار إلى الحاوية
        notificationContainer.prepend(notificationElement); // لإظهار الأحدث في الأعلى

        // إزالة الإشعار بعد 5 ثوانٍ
        setTimeout(() => {
            notificationElement.classList.add('animate-fade-out-up');
            notificationElement.addEventListener('animationend', () => {
                notificationElement.remove();
            });
        }, 5000);
    }

    /**
     * وظيفة لتحديث عدد الإشعارات (مثال).
     * يمكنك تحديث عنصر HTML يعرض عدد الإشعارات غير المقروءة.
     */
    function updateNotificationCount() {
        const notificationCountElement = document.getElementById('notification-count');
        if (notificationCountElement) {
            let currentCount = parseInt(notificationCountElement.textContent) || 0;
            notificationCountElement.textContent = currentCount + 1;
            // يمكنك أيضاً إضافة فئة CSS لجعلها تبرز
            notificationCountElement.classList.add('bg-red-500', 'text-white', 'rounded-full', 'px-2', 'py-1', 'text-xs');
        }
    }

    // ابدأ الاتصال بـ WebSocket عند تحميل الصفحة
    connectWebSocket();
});

// أضف بعض أنماط Tailwind CSS للرسوم المتحركة (يمكن وضعها في ملف CSS منفصل)
// هذه الأنماط ستجعل الإشعارات تظهر وتختفي بشكل سلس.
const style = document.createElement('style');
style.innerHTML = `
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeOutUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }

    .animate-fade-in-down {
        animation: fadeInDown 0.5s ease-out forwards;
    }

    .animate-fade-out-up {
        animation: fadeOutUp 0.5s ease-in forwards;
    }
`;
document.head.appendChild(style);