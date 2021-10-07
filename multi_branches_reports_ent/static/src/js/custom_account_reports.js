odoo.define('multi_branches_reports_ent.account_report_generic', function (require) {
'use strict';

var account_report_generic = require('account_reports.account_report');

    account_report_generic.include({
        render_searchview_buttons: function() {
            var self = this;
            this._super();

            console.log(self.report_options)
            // Branch filter
            this.$searchview_buttons.find('.js_branch_auto_complete').select2();
            self.$searchview_buttons.find('[data-filter="branch_ids"]').select2("val", self.report_options.branch_ids);

            this.$searchview_buttons.find('.js_branch_auto_complete').on('change', function(){
                self.report_options.branch_ids = self.$searchview_buttons.find('[data-filter="branch_ids"]').val();
                return self.reload().then(function(){
                    self.$searchview_buttons.find('.account_branch_filter').click();
                })
            });
        }
    });
});
