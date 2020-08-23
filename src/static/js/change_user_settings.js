/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, log, validate */

$(function() {

    "use strict";

    const BACKGROUND_COLOURS = {
        "asm":              "#ffffff",
        "base":             "#ffffff",
        "black-tie":        "#333333",
        "blitzer":          "#cc0000",
        "cupertino":        "#deedf7",
        "dark-hive":        "#444444",
        "dot-luv":          "#0b3e6f",
        "eggplant":         "#30273a",
        "excite-bike":      "#f9f9f9",
        "flick":            "#dddddd",
        "hot-sneaks":       "#35414f",
        "humanity":         "#cb842e",
        "le-frog":          "#3a8104",
        "mint-choc":        "#453326",
        "overcast":         "#dddddd",
        "pepper-grinder":   "#ffffff",
        "redmond":          "#5c9ccc",
        "smoothness":       "#cccccc",
        "south-street":     "#ece8da",
        "start":            "#2191c0",
        "sunny":            "#817865",
        "swanky-purse":     "#261803",
        "trontastic":       "#9fda58",
        "ui-darkness":      "#333333",
        "ui-lightness":     "#ffffff",
        "vader":            "#888888"
    };

    const change_user_settings = {

        /** Where we have a list of pairs, first is value, second is label */
        two_pair_options: function(o, isflag) {
            let s = [];
            $.each(o, function(i, v) {
                let ds = "";
                if (isflag) {
                    ds = 'data-style="background-image: url(static/images/flags/' + v[0] + '.png)"';
                }
                s.push('<option value="' + v[0] + '" ' + ds + '>' + v[1] + '</option>');
            });
            return s.join("\n");
        },

        render: function() {
            return [
                html.content_header(_("Change User Settings")),
                '<table class="asm-table-layout">',
                '<tr>',
                    '<td>' + _("Username") + '</td>',
                    '<td>' + asm.user + '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="realname">' + _("Real name") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="realname" data="realname" class="asm-textbox" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="email">' + _("Email Address") + '</label>',
                    '</td>',
                    '<td>',
                    '<input id="email" data="email" class="asm-textbox" />',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="systemtheme">' + _("Visual Theme") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="systemtheme" data="theme" class="asm-selectbox">',
                    '<option value="">' + _("(use system)") + '</option>',
                    this.two_pair_options(controller.themes),
                    '</select>',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="olocale">' + _("Locale") + '</label>',
                    '</td>',
                    '<td>',
                    '<select id="olocale" data="locale" class="asm-doubleselectbox asm-iconselectmenu">',
                    '<option value="" data-style="background-image: url(static/images/flags/' + config.str("Locale") + '.png)">' + _("(use system)") + '</option>',
                    this.two_pair_options(controller.locales, true),
                    '</select>',
                    '</td>',
                '</tr>',
                '<tr>',
                    '<td>',
                    '<label for="signature">' + _("Signature") + '</label>',
                    '<button id="button-change" type="button" style="vertical-align: middle">' + _("Clear and sign again") + '</button>',
                    '</td>',
                    '<td>',
                    '<div id="signature" style="width: 500px; height: 200px; display: none" />',
                    '<img id="existingsig" style="display: none; border: 0" />',
                    '</td>',
                '</tr>',
                '</table>',
                '<div class="centered">',
                    '<button id="save">' + html.icon("save") + ' ' + _("Save") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            try {
                $("#signature").signature({ guideline: true });
                $("#button-change")
                    .button({ icons: { primary: "ui-icon-pencil" }, text: false })
                    .click(function() {
                        $("#existingsig").hide();
                        $("#signature").show();
                        $("#signature").signature("clear");
                    });
            }
            catch (excanvas) {
                log.error("failed creating signature canvas");   
            }

            $("#save").button().click(async function() {
                $(".asm-content button").button("disable");
                header.show_loading();
                let formdata = $("input, select").toPOST();
                try {
                    if (!$("#signature").signature("isEmpty")) {
                        formdata += "&signature=" + encodeURIComponent($("#signature canvas").get(0).toDataURL("image/png"));
                    }
                } catch (excanvas) {
                    log.error("failed reading signature canvas", excanvas);
                }
                try {
                    await common.ajax_post("change_user_settings", formdata);
                    common.route("main", true);
                }
                catch(err) {
                    log.error(err, err);
                    $(".asm-content button").button("enable");
                }
            });

            // When the visual theme is changed, switch the CSS file so the
            // theme updates immediately.
            $("#systemtheme").change(function() {
                let theme = $("#systemtheme").val();
                if (theme == "") {
                    theme = asm.theme;
                }
                let href = asm.jqueryuicss.replace("%(theme)s", theme);
                $("#jqt").attr("href", href);
                $("body").css("background-color", BACKGROUND_COLOURS[theme]);
            });

        },

        sync: function() {
            let u = controller.user[0];
            $("#realname").val(html.decode(u.REALNAME));
            $("#email").val(u.EMAILADDRESS);
            $("#olocale").select("value", u.LOCALEOVERRIDE);
            $("#systemtheme").select("value", u.THEMEOVERRIDE);
            if (controller.sigtype != "touch") { 
                $("#signature").closest("tr").hide(); 
            }
            if (u.SIGNATURE) {
                $("#signature").hide();
                $("#existingsig").attr("src", u.SIGNATURE).show();
            }
            else {
                $("#existingsig").hide();
                $("#signature").show();
            }
        },

        name: "change_user_settings",
        animation: "options",
        autofocus: "#realname",
        title: function() { return _("Change User Settings"); },
        routes: {
            "change_user_settings": function() { common.module_loadandstart("change_user_settings", "change_user_settings"); }
        }

    };

    common.module_register(change_user_settings);

});
