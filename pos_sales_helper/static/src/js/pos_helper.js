odoo.define('pos_sales_helper.pos_helper', function (require) {
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
                self.helpers = records;
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
            this.helper_id = json.helper_id;
            _super_order.init_from_JSON.call(this, json);
        },
        export_as_JSON: function() {
            var order = _super_order.export_as_JSON.apply(this,arguments);
            return _.extend(order, {
                'helper_id': this.helper_id,
            })
        },
    });

    var Helper = PopupWidget.extend({
        template: 'HelperSelect',

        renderElement: function () {
            var self = this;
            this._super();
            this.$('.myfilterhelper').on('input', function (){
                var input, filter, table, tr, td, i, txtValue,count=0;
                input = document.getElementById("helperInput");
                filter = input.value.toUpperCase();
                table = document.getElementById("myTablehelper");
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
                    document.getElementById('helper_id').value=id
                    this.origColor=this.style.backgroundColor;
                    this.style.backgroundColor='#BCD4EC';
                    this.hilite = true;                }
                else{
                    this.style.backgroundColor=this.origColor;
                    this.hilite = false;
                    document.getElementById('helper_id').value=""
                }
            });
        },

        click_confirm: function(){
            var Order = this.pos.get_order();
            var helper_id = document.getElementById('helper_id').value;
            Order.helper_id = helper_id;
            this.gui.close_popup();
        },
        
    });

    gui.define_popup({
        'name': 'helper', 
        'widget': Helper,
    });
    
    var HelperSelection = screens.ActionButtonWidget.extend({
        template: 'HelperButton',
        button_click: function () {
            this._super(event);
            var self = this;
            if (self.pos.helpers){
                self.gui.show_popup('helper',{});
            }
        }
    }
    );

    screens.define_action_button({
        'name': 'HelperSelection',
        'widget': HelperSelection,
        'condition': function () {
            return true;
        },
    });

});