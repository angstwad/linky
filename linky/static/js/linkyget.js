$.ajax({
    type: "post",
    data:{
        title: document.title,
        url: document.URL
    },
    url: "http://localhost:5000/user/e366c90e384fbea6772be69fd22f8573fe8b5708/send"
});

