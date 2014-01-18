String.prototype.trim = function() { return this.replace(/^\s+|\s+$/g, ''); };

$(document).ready(function(){

var output = document.getElementById('output')

var stats = {
    1:'',
    2:'此URL不能识别\n请输入单个相册的页面地址！',
    3:'请确认，在没有登陆的情况下依旧可以访问此相册吗？'
}

function draw(response){
    if(response.stats==1){
        output.value = response.imgUrls;
        $('#albumcover').attr('src',response.imgBase64);
        $('#albumtitle').html(response.title+'有'+response.hasPics+'张图片');
        $('#albumpics').html('抓取出'+response.getPics+'张图片');
    }else{
        output.value = stats[response.stats];
    }    
}

$('#crawl').bind('click',function(){
    var url = document.getElementById('input').value.trim();
    if(url){
        document.getElementById('load').style.visibility = 'visible ';
        document.getElementById('output').value = '';
        $.post('/url',{url: url},'json')
        .done(function(response){draw(response)})
        .fail(function(response){output.value = 'error!';})
        .always(function(){document.getElementById('load').style.visibility='hidden';});
    };
});

});
