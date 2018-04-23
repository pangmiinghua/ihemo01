function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // TODO: 在页面加载完毕之后获取区域信息
    $.get('/api/1.0/areas',function (response) {
       if (response.errno == '0') {
           // $.each(response.data,function (i,area) {
           //     $('#area-id').append('<option value="'+area.aid+'">'+area.aname+'</option>>');
           // });

           // 使用art-template模板引擎中的js生成要渲染的html内容
            var html = template('areas-tmpl', {'areas':response.data});
            // 将生成的html赋值给某个标签
            $('#area-id').html(html);
       }else {
           alert(response.errmsg);
       }
    });

    // TODO: 处理房屋基本信息提交的表单数据
    $('#form-house-info').submit(function (event) {
        event.preventDefault();

        var params = {};   //定义字典    map函数是对其循环
        $(this).serializeArray().map(function (obj) {
            params[obj.name] = obj.value;
        });

        facilities = [];  //定义列表
        // params['title'] = title;
        // 收集界面中所有被选中的checkbox，而且name必须等于facility
        $(':checkbox:checked[name=facility]').each(function (i,elem) {
            facilities[i] = elem.value;    //往列表添加元素的格式
        });
        params['facility'] = facilities;
        console.log(params);

        $.ajax({
            url:'/api/1.0/houses',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0'){
                    $('#form-house-info').hide();
                    $('#form-house-image').show();
                    //将发布成功的house_id渲染到界面上
                    $('#house-id').val(response.data.house_id);
                }else if(response.errno == '4101'){
                    location.href = 'login.html'
                }else {
                    alert(response.errmsg);
                }
            }
        });

    });
    // TODO: 处理图片表单的数据
    $('#form-house-image').submit(function (event) {
        event.preventDefault();

        $(this).ajaxSubmit({
            url:"/api/1.0/houses/image",
            type:'post',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0'){
                    $('.house-image-cons').append('<img src="'+response.data.house_image_url+'">')
                }else if (response.errno == '4101'){
                    location.href = "/";
                }else {
                    alert(response.errmsg);
                }
            }
        });
    });
});

