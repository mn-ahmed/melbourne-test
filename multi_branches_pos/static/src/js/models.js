odoo.define('multi_branches_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields("pos.session", ["branch_id"]);
});
