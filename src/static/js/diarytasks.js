/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const diarytasks = {

        model: function() {
            const dialog = {
                add_title: _("Add diary task"),
                edit_title: _("Edit diary task"),
                edit_perm: 'edt',
                helper_text: _("Diary tasks need a name."),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "NAME", post_field: "name", label: _("Name"), type: "text", validation: "notblank" },
                    { json_field: "RECORDTYPE", post_field: "type", label: _("Type"), type: "select", options: 
                        '<option value="0">' + _("Animal") + '</option>' +
                        '<option value="1">' + _("Person") + '</option>' }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    await tableform.fields_post(dialog.fields, "mode=update&diarytaskid=" + row.ID, "diarytasks");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                columns: [
                    { field: "NAME", display: _("Name"), initialsort: true, formatter: function(row) {
                        return "<span style=\"white-space: nowrap\">" + 
                            "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                            "<a href=\"diarytask?taskid=" + row.ID + "\">" + row.NAME + "</a> " +
                            "<button class=\"link-edit\" data-icon=\"pencil\" data-id=\"" + row.ID + "\">" + _("Edit diary task") + "</button>" +
                            "</span>";
                    }},
                    { field: "RECORDTYPE", display: _("Type"), formatter: function(row) { return row.RECORDTYPE == 0 ? _("Animal") : _("Person"); }},
                    { field: "NUMBEROFTASKS", display: _("Number of Tasks") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New diary task"), icon: "new", enabled: "always", 
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "diarytasks");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("diarytasks", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Diary Tasks"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "diarytasks",
        animation: "book",
        title: function() { return _("Diary Tasks"); },
        
        routes: {
            "diarytasks": function() { 
                common.module_loadandstart("diarytasks", "diarytasks");
            }
        }

    };
    
    common.module_register(diarytasks);

});
