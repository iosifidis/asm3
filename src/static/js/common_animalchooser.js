/*global $, jQuery */
/*global asm, common, config, dlgfx, format, html, header, log, validate, _, escape, unescape */

"use strict";

/**
 * Animal chooser widget. To create one, use a hidden input
 * with a class of asm-animalchooser
 *
 * <input id="animal" class="asm-animalchooser" data="boundfield" type="hidden" value="initialid" />
 *
 * callbacks: loaded (after loadbyid is complete)
 *            change (after user has clicked on a new selection)
 *            cleared (after user clicks the clear button)
 */
$.widget("asm.animalchooser", {

    selected: null,

    options: {
        id: 0,
        rec: {},
        node: null,
        dialog: null,
        display: null,
        filter: "all"
    },

    _create: function() {
        var h = [
            '<div class="animalchooser">',
            '<input class="animalchooser-oopostcode" type="hidden" value="" />',
            '<input class="animalchooser-bipostcode" type="hidden" value = "" />',
            '<table style="margin-left: 0px; margin-right: 0px; width: 100%">',
            '<tr>',
            '<td class="animalchooser-display">',
            '</td>',
            '<td valign="top" align="right">',
            '<button class="animalchooser-link-find">' + _("Select an animal") + '</button>',
            '<button class="animalchooser-link-clear">' + _("Clear") + '</button>',
            '</td>',
            '</tr>',
            '</table>',
            '<div class="animalchooser-find" style="display: none" title="' + html.title(_("Find animal")) + '">',
            '<input type="text" class="asm-textbox" />',
            '<button>' + _("Search") + '</button>',
            '<img style="height: 16px" src="static/images/wait/rolling_3a87cd.svg" />',
            '<table width="100%">',
            '<thead>',
                '<tr class="ui-widget-header">',
                    '<th></th>',
                    '<th>' + _("Name") + '</th>',
                    '<th>' + _("Code") + '</th>',
                    '<th>' + _("Microchip") + '</th>',
                    '<th>' + _("Type") + '</th>',
                    '<th>' + _("Species") + '</th>',
                    '<th>' + _("Breed") + '</th>',
                    '<th>' + _("Sex") + '</th>',
                '</tr>',
            '</thead>',
            '<tbody></tbody>',
            '</table>',
            '</div>',
            '</div>'
        ].join("\n");
        var node = $(h);
        var self = this;
        this.options.node = node;
        var dialog = node.find(".animalchooser-find");
        this.options.dialog = dialog;
        this.options.display = node.find(".animalchooser-display");
        this.element.parent().append(node);
        // Set the filter
        if (this.element.attr("data-filter")) { 
            this.options.filter = this.element.attr("data-filter");
        }
        // Create the dialog
        var acbuttons = {};
        acbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
        dialog.dialog({
            autoOpen: false,
            height: 400,
            width: 800,
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: acbuttons
        });
        dialog.find("table").table({ sticky_header: false });
        dialog.find("input").keydown(function(event) { if (event.keyCode == 13) { self.find(); return false; }});
        dialog.find("button").button().click(function() { self.find(); });
        dialog.find("img").hide();
        // Bind the find button
        node.find(".animalchooser-link-find")
            .button({ icons: { primary: "ui-icon-search" }, text: false })
            .click(function() {
                dialog.dialog("open");
            });
        // Bind the clear button
        node.find(".animalchooser-link-clear")
            .button({ icons: { primary: "ui-icon-trash" }, text: false })
            .click(function() {
                self.clear(true);
            });
        // Was there a value already set by the markup? If so, use it
        if (self.element.val() != "" && self.element.val() != "0") {
            self.loadbyid(self.element.val());
        }
    },

    /**
     * Empties the widget
     */
    clear: function(fireclearedevent) {
        this.selected = null;
        this.element.val("0");
        this.options.id = 0;
        this.options.rec = {};
        this.options.display.html("");
        if (fireclearedevent) { this._trigger("cleared", null); }
    },

    is_empty: function() {
        return this.selected == null;
    },

    destroy: function() {
        try {
            this.options.dialog.dialog("destroy");
        } catch (ex) {}
    },

    /**
     * Loads an animal into the widget by ID
     */
    loadbyid: function(animalid) {
        if (!animalid || animalid == "0" || animalid == "") { return; }
        this.clear();
        this.element.val(animalid);
        var self = this;
        var formdata = "mode=id&id=" + animalid;
        $.ajax({
            type: "POST",
            url:  "animal_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                var h = "";
                var animal = jQuery.parseJSON(data);
                var rec = animal[0];
                var disp = "<a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.CODE + " - " + rec.ANIMALNAME + "</a>";
                self.element.val(rec.ID);
                self.options.rec = rec;
                self.options.display.html(disp);
                self._trigger("loaded", null, rec);
                self.selected = rec;
                common.inject_target();
            },
            error: function(jqxhr, textstatus, response) {
                log.error(response);
            }
        });
    },

    find: function() {
        var self = this;
        var dialog = this.options.dialog, node = this.options.node;
        dialog.find("img").show();
        dialog.find("button").button("disable");
        var formdata = "mode=find&filter=" + encodeURIComponent(this.options.filter) + "&q=" + encodeURIComponent(dialog.find("input").val());
        $.ajax({
            type: "POST",
            url:  "animal_embed",
            data: formdata,
            dataType: "text",
            success: function(data, textStatus, jqXHR) {
                var h = "";
                var animal = jQuery.parseJSON(data);
                // Create the table content from the results
                $.each(animal, function(i, a) {
                    h += "<tr>";
                    h += "<td>" + html.animal_emblems(a, {showlocation: true}) + "</td>";
                    h += "<td><a href=\"#\" data=\"" + i + "\">" + a.ANIMALNAME + "</a></td>";
                    h += "<td>" + a.CODE + "</td>";
                    h += "<td>" + a.IDENTICHIPNUMBER + "</td>";
                    h += "<td>" + a.ANIMALTYPENAME + "</td>";
                    h += "<td>" + a.SPECIESNAME + "</td>";
                    h += "<td>" + a.BREEDNAME + "</td>";
                    h += "<td>" + a.SEXNAME + "</td>";
                    h += "</tr>";
                });
                dialog.find("table > tbody").html(h);
                // Remove any existing events from previous searches
                dialog.off("click", "a");
                // Use delegation to bind to the name column and select
                // the animal once clicked. Triggers the change callback
                dialog.on("click", "a", function(e) {
                    var rec = animal[$(this).attr("data")];
                    self.element.val(rec.ID);
                    self.options.rec = rec;
                    var disp = "<a class=\"asm-embed-name\" href=\"animal?id=" + rec.ID + "\">" + rec.CODE + " - " + rec.ANIMALNAME + "</a>";
                    self.options.display.html(disp);
                    node.find(".animalchooser-oopostcode").val(rec.ORIGINALOWNERPOSTCODE);
                    node.find(".animalchooser-bipostcode").val(rec.BROUGHTINBYOWNERPOSTCODE);
                    try { validate.dirty(true); } catch(ex) { }
                    dialog.dialog("close");
                    self._trigger("change", null, rec);
                    self.selected = rec;
                    common.inject_target();
                    return false;
                });
                // Force the table to update itself and remove the spinner
                dialog.find("table").trigger("update");
                dialog.find("img").hide();
                dialog.find("button").button("enable");
            },
            error: function(jqxhr, textstatus, response) {
                dialog.dialog("close");
                log.error(response);
                dialog.find("img").hide();
                dialog.find("button").button("enable");
            }
        });
    },

    get_selected: function() {
        return this.selected;
    }

});

