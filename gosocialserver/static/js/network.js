function like(postId,likeTagId,disLikeTagId){
    post('/posts/'+postId+'/like',postId,
    function(data,status,xhr){
        var spliteData = data.splite('|');
        document.getElementById(likeTagId).innerHTML = spliteData[0];
        document.getElementById(disLikeTagId).innerHTML = spliteData[1];
    })
}
function disLike(postId,disLikeTagId,likeTagId){
    post('/posts/'+postId+'/disLike',postId,
    function(data,status,xhr){
        var spliteData = data.splite('|');
        document.getElementById(disLikeTagId).innerHTML = spliteData[0];
        document.getElementById(likeTagId).innerHTML = spliteData[1];
    })
}