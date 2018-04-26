function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    // TODO: 判断用户是否登录
    $.get('/api/1.0/sessions', function (response) {
        if (!(response.data.user_id && response.data.name)) {
           location.href = 'login.html'
        }
    });

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg("日期有误，请重新选择!");
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd)/(1000*3600*24) + 1;
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    // TODO: 获取房屋的基本信息
    $.get('/api/1.0/houses/'+houseId, function (response) {
        if (response.errno == '0') {
            $('.house-info>img').attr('src', response.data.img_urls[0]);
            $('.house-text>h3').html(response.data.title);
            $('.house-text span').html((response.data.price/100).toFixed(2));
        } else {
            alert(response.errmsg);
        }
    });

    // TODO: 订单提交
    //给'提交订单'的span标签，添加点击事件，并监听
    $('.submit-btn').on('click',function () {

        //获取input标签中的入住和离开时间
        var stsrt_data = $('#start-date').val();
        var end_data = $('#end-date').val();
        if (!stsrt_data){
            alert("请输入入住时间");
            return;
        }
        if (!end_data){
            alert('请输入离开时间');
            return;
        }
        var params = {
            'house_id':houseId,
            'start_data':stsrt_data,
            'end_data':end_data
        };
        $.ajax({
            url: '/api/1.0/orders',
            type: 'post',
            data: JSON.stringify(params),
            contentType: 'application/json',
            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0') {
                    // 提交订单成功，进入"我的订单"
                    location.href = 'orders.html';
                } else if (response.errno == '4101') {
                    location.href = 'login.html';
                } else {
                    alert(response,errmsg);
                }
            }
        });
    });
});
