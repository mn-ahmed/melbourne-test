odoo.define('pos_sales_helper.sales_man', function (require) {
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var chrome = require('point_of_sale.chrome');
    var qweb = core.qweb;

    models.load_models([
        {
            model: "hr.employee",
            fields: ["id", "name"],
            domain: function(self){ return [['active','=', true]];},
            loaded: function(self, records) {
                self.sales_mans = records;
            }
        },
    ]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr,options){
            _super_order.initialize.call(this, attr, options);
            this.sales_man_id = false;
        }, 

        init_from_JSON: function(json) {
            this.sales_man_id = json.sales_man_id;
            _super_order.init_from_JSON.call(this, json);
        },
        export_as_JSON: function() {
            var order = _super_order.export_as_JSON.apply(this,arguments);
            return _.extend(order, {
                'sales_man_id': this.sales_man_id,
            })
        },
    });

    var SalesMan = PopupWidget.extend({
        template: 'SalesManSelect',
        
        renderElement: function () {
            var self = this;
            this._super();
            this.$('.myfiltersales').on('input', function (){
                var input, filter, table, tr, td, i, txtValue,count=0;
                input = document.getElementById("salesInput");
                filter = input.value.toUpperCase();
                table = document.getElementById("myTablesales");
                tr = table.getElementsByTagName("tr");
                for (i = 0; i < tr.length; i++) {
                    td = tr[i].getElementsByTagName("td")[0];
                    if (td) {
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            tr[i].style.display = "";
                            if (count == 0) {
                                tr[i].style.backgroundColor='#FFFFFF';
                                count = count +1;
                            }
                            else {
                                count = count -1;
                                tr[i].style.backgroundColor='#e0e0eb';
                            }
                        } else {
                            tr[i].style.display = "none";
                        }
                    }
                              
                } 
            }),
            this.$('.line-index').on('click', function (){
                if(!this.hilite){
                    var rowsNotSelected = document.getElementsByTagName('tr');
                    for (var row = 0; row < rowsNotSelected.length; row++) {
                        rowsNotSelected[row].style.backgroundColor = "";
                    }
                    var id = parseInt($(this).attr('id'));
                    document.getElementById('sales_id').value=id
                    this.origColor=this.style.backgroundColor;
                    this.style.backgroundColor='#BCD4EC';
                    this.hilite = true;                }
                else{
                    this.style.backgroundColor=this.origColor;
                    this.hilite = false;
                    document.getElementById('sales_id').value=""
                }
            });
        },

        click_confirm: function(){
            var Order = this.pos.get_order();
            var sales_man_id = document.getElementById('sales_id').value;
            Order.sales_man_id = sales_man_id;
            this.gui.close_popup();
        }
    });

    gui.define_popup({
        'name': 'sale-man', 
        'widget': SalesMan,
    });
    
    var SalesManSelection = screens.ActionButtonWidget.extend({
        template: 'SalesManButton',
        button_click: function () {
            this._super(event);
            var self = this;
            if (self.pos.sales_mans){
                self.gui.show_popup('sale-man',{});
            }
        }
    }
    );

    screens.define_action_button({
        'name': 'SalesManSelection',
        'widget': SalesManSelection,
        'condition': function () {
            return true;
        },
    });

});