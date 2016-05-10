function like(postId, likeTagId, disLikeTagId) {
    $.get('/posts/' + postId + '/like', postId,
        function (data, status, xhr) {
            if (data.length > 20) {
                window.location.href = "/auth/login";
                return;
            }

            var splitData = data.split('|');
            document.getElementById(likeTagId).innerHTML = splitData[0];
            document.getElementById(disLikeTagId).innerHTML = splitData[1];
        })
}
function disLike(postId, disLikeTagId, likeTagId) {
    $.get('/posts/' + postId + '/dislike', postId,
        function (data, status, xhr) {
            if (data.length > 20) {
                window.location.href = "/auth/login";
                return;
            }

            var splitData = data.split('|');
            document.getElementById(disLikeTagId).innerHTML = splitData[0];
            document.getElementById(likeTagId).innerHTML = splitData[1];
        })
}


function sendComment(postId, parentId, body, callback) {
    var url = '/posts/' + postId.toString() + '/comments/add' + (parentId != null) ? '/' + parentId.toString() : '';
    $.post(url, {body: body.toString()},
        function (data, status, xhr) {
            if (xhr.status == 200) {
                callback(data);
            }
        });
}