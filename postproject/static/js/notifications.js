document.addEventListener('DOMContentLoaded', function () {
    // 1. More robust user authentication check
    if (!window.currentUser?.isAuthenticated) {
        console.warn("User not authenticated - notifications disabled");
        return;
    }

    console.log("Connecting WebSocket for user ID:", window.currentUser.id);

    // 2. Cache DOM elements at the start
    const notificationBell = document.getElementById('notificationBell');
    const notificationCountEl = document.getElementById('notificationCount');
    const notificationList = document.getElementById('notificationList');
    const notificationDropdown = document.getElementById('notificationDropdown');

    if (!notificationBell || !notificationCountEl || !notificationList || !notificationDropdown) {
        console.error("Required notification elements not found");
        return;
    }

    // 3. WebSocket connection with error handling
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsPath = `${protocol}//${window.location.host}/ws/notifications/`;
    console.log("Connecting to:", wsPath);

    let socket;
    let notificationCount = 0;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000; // 3 seconds

    function connectWebSocket() {
        try {
            socket = new WebSocket(wsPath);
            
            socket.onopen = function() {
                console.log("WebSocket connected successfully");
                reconnectAttempts = 0; // Reset on successful connection
            };

            socket.onmessage = handleNotification;
            socket.onclose = handleDisconnect;
            socket.onerror = handleError;
            
        } catch (error) {
            console.error("WebSocket initialization error:", error);
            scheduleReconnect();
        }
    }

    function handleNotification(event) {
        try {
            const data = JSON.parse(event.data);
            if (!data.message) {
                throw new Error("Invalid notification format");
            }

            console.log("New notification:", data);
            notificationCount++;
            
            // Update counter
            notificationCountEl.textContent = notificationCount;
            notificationCountEl.style.display = 'inline';
            
            // Add notification to list
            const notificationItem = createNotificationItem(data);
            notificationList.prepend(notificationItem);
            
            // Visual feedback
            flashNotificationBell();
            
        } catch (error) {
            console.error("Notification processing error:", error);
        }
    }

    function createNotificationItem(data) {
        const item = document.createElement('li');
        item.className = 'notification-item';
        item.textContent = data.message;
        
        if (data.postId) {
            item.style.cursor = 'pointer';
            item.addEventListener('click', () => {
                window.location.href = `/post/${data.postId}`;
            });
        }
        
        return item;
    }

    function flashNotificationBell() {
        notificationBell.style.color = 'red';
        setTimeout(() => {
            notificationBell.style.color = '';
        }, 1000);
    }

    function handleDisconnect(event) {
        console.log(`WebSocket disconnected (code: ${event.code}, reason: ${event.reason}`);
        if (event.code !== 1000) { // Don't reconnect if closed normally
            scheduleReconnect();
        }
    }

    function handleError(error) {
        console.error("WebSocket error:", error);
        socket.close(); // Ensure clean closure
    }

    function scheduleReconnect() {
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            const delay = reconnectDelay * Math.min(reconnectAttempts, 3); // Exponential backoff
            console.log(`Reconnecting attempt ${reconnectAttempts} in ${delay}ms...`);
            setTimeout(connectWebSocket, delay);
        } else {
            console.error("Max reconnection attempts reached");
            notificationBell.title = "Notifications (disconnected)";
            notificationBell.style.color = 'gray';
        }
    }

    // 4. Improved dropdown interaction
    notificationBell.addEventListener('click', function(e) {
        e.stopPropagation();
        notificationDropdown.style.display = 
            notificationDropdown.style.display === 'block' ? 'none' : 'block';
        
        if (notificationDropdown.style.display === 'block') {
            notificationCount = 0;
            notificationCountEl.style.display = 'none';
        }
    });

    document.addEventListener('click', function(e) {
        if (!notificationBell.contains(e.target)) {
            notificationDropdown.style.display = 'none';
        }
    });

    // 5. Initial connection
    connectWebSocket();

    // 6. Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close(1000, "Page unloading");
        }
    });
});