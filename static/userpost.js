$.ajax({
    url: 'http://dev.rackspace.com:5000/user/688f3b8e794c4bb4b42858044dd29c1e/send',
    type: 'post',
    data: {
        url: document.URL,
        title: document.title
    },
    success: function(data, status) {
      console.log(data)
    },
    error: function(data, status) {
        console.log(data)
    }
})