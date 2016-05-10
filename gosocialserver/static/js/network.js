function like(postId, likeTagId, disLikeTagId) {
    $.get('/posts/' + postId + '/like', postId,
        function (data, status, xhr) {
            var splitData = data.split('|');
            document.getElementById(likeTagId).innerHTML = splitData[0];
            document.getElementById(disLikeTagId).innerHTML = splitData[1];
        })
}
function disLike(postId, disLikeTagId, likeTagId) {
    $.get('/posts/' + postId + '/dislike', postId,
        function (data, status, xhr) {
            var splitData = data.split('|');
            document.getElementById(disLikeTagId).innerHTML = splitData[0];
            document.getElementById(likeTagId).innerHTML = splitData[1];
        })
}