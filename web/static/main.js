String.prototype.trim = function() { return this.replace(/^\s+|\s+$/g, ''); };

$(document).ready(function(){

var output = document.getElementById('output')

var states = {
    '-1':'此URL不能识别\n请输入单个相册的页面地址!\nurl like this:http://my.hupu.com/sunyatsen/photo/a135716.html',
    '0': '空相册,什么都没有找到？',
    '1': '抓取完成',
    '4': 'user id non-existent',
    '302': '请确认，此相册只否公开，还是只对好友公开?\n指定用户抓取，请使用高级功能',
    '403': 'login fail',
    '501': '暂不支持抓取加密相册',

}

function draw(response){
    if(response.state == 1 || response.state == 0){
        output.value = response.pics_urls;
        $('#albumcover').attr('src',response.cover);
        $('#albumtitle').html('《'+response.title+'》'+'有'+response.pics+'张图片');
        $('#albumpics').html('抓取出'+response.get_pics+'张图片');
    }else{
        output.value = states[response.state];
    }    
}

function cleardraw(){
    output.value = '';
    $('#albumcover').attr('src','');
    $('#albumtitle').html('');
    $('#albumpics').html('');
}

$('#crawl').bind('click',function(){
    cleardraw()
    var url = $('input[name=albumurl]').val().trim();
    var load = document.getElementById('load');
    if(url){
        load.style.display = 'block';
        document.getElementById('output').value = '';
        if($('input[name=username]').length>0 && $('input[name=password]').length>0){
            var data = {
                url: url,
                user: $('input[name=username]').val(),
                password: $('input[name=password]').val()
            };      
        }else{
            var data = {url: url};
        }
        $.post('/getalbum',data,'json')
        .done(function(response){draw(response)})
        .fail(function(response){output.value = 'server fail'})
        .always(function(){load.style.display ='none'});
    };
});

// login model
var m = $('#loginModel');
$('html').click(function() {
    m.hide()
});
$("#loginModel").click(function(){
    event.stopPropagation();
})
$("[href='#login-model']").click(function(){
    event.stopPropagation();
    if(m.css('display') == 'none'){
        m.css('display','block');
    }else{
        m.css('display','none');
    }
})

});
