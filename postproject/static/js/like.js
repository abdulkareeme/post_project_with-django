document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const csrfToken = this.dataset.csrfToken;
            const likeCountElement = this.nextElementSibling;
            const likeButton = this;

            fetch(`/toggle-like/${postId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update button appearance
                if (data.liked) {
                    likeButton.classList.add('liked');
                    likeButton.innerHTML = '❤️';
                } else {
                    likeButton.classList.remove('liked');
                    likeButton.innerHTML = '🤍';
                }
                
                // Update like count
                likeCountElement.textContent = `${data.likes_count} like${data.likes_count !== 1 ? 's' : ''}`;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});