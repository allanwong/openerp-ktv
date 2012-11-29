$(document).ready(function() {
	var openerp, ktv_room_point;
	openerp = window.openerp.init();
	window.openerp.web.core(openerp);
	window.openerp.web.chrome(openerp);
	window.openerp.web.data(openerp);
	window.openerp.ktv_sale(openerp);

    //自服务器端获取数据后才执行测试
	$.when(openerp.connection.bind(), openerp.connection.session_authenticate("ktv_test", "admin", "1", false), function() {
		ktv_room_point = openerp.ktv_sale.ktv_room_point = new openerp.ktv_sale.model.KtvRoomPoint();
	}()).then(function() {
		module("ktv_sale model 测试", {
			setup: function() {},
			teardown: function() {}
		});
		asyncTest("应能正确获取fee_type对象", 1, function() {
			var fee_types = new openerp.ktv_sale.model.FeeTypeCollection();
			openerp.ktv_sale.model.FeeType.fetch().pipe(function(result) {
				fee_types.add(result);
			});
			setTimeout(function() {
				ok(fee_types.length > 0);
				start(1);
			},
			150);
		});
		test("应能够正确初始化ktv_room_point", 1, function() {
			ok(ktv_room_point.get('all_rooms').length > 0);
		});
        asyncTest("应能够正确初始化RoomFeeInfo对象",1,function(){
            var room = ktv_room_point.get("all_rooms").at(0);
            var room_fee_info = new openerp.ktv_sale.model.RoomFeeInfo({"room" : room});
            setTimeout(function(){
                test = room_fee_info.get("all_hourly_fee_discount_lines").length > 0;
                ok(test > 0);
                start();
            },150);
        });
	});
});

