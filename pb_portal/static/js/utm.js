var urlRegex = new RegExp(/^(https?:\/\/)?((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))(:\d+)?(\/[-a-z\d%_.~+]*)*(\?[;&a-z\d%_.~+=-]*)?(\#[-a-z\d_]*)?$/i);
var companyNameRegex = /^[a-z0-9_]+$/;
var is_adv = false;
var _url_utm_info = '';
var _url_get_utm = '';
var _url_last_10_utms = '';
var _info;

const set_default = function (url_utm_info, url_get_utm, url_last_10_utms) {
    decs_manage('');
    _url_utm_info = url_utm_info;
    _url_get_utm = url_get_utm;
    _url_last_10_utms = url_last_10_utms;
    set_start_value(_url_utm_info);
    $('#page_content').hide();
    $('#user').on('change', function () {
        user_control();
    });
    $('#target_url').on('change', function () {
        validate_url();
    });
    $('#check_adv').on('click', function () {
        check_adv();
    });
    $('#product_type').on('focus', function () {
        decs_manage('product_type');
    });
    $('#page_type').on('focus', function () {
        decs_manage('page_type');
    });
    $('#medium').on('focus', function () {
        decs_manage('medium');
    });
    $('#source').on('focus', function () {
        decs_manage('source');
    });
    $('#campaign_name').on('focus', function () {
        decs_manage('campaign_name');
    });
    $('#content').on('focus', function () {
        decs_manage('content');
    });
    $('#project').on('focus', function () {
        decs_manage('project');
    });
    $('#medium').on('change', function () {
        update_source();
    });
    $('#get_utm').on('click', function () {
        get_utm();
    });
    $('#campaign_name').on('change', function () {
        validate_campaign_name();
    });
}

const user_control = function () {
    if ($('#user').val() != '') {
        $('#page_content').show();
    } else {
        $('#page_content').hide();
    }
};

const validate_url = function () {
    $('#target_url').removeClass('is-invalid');
    $('#target_url').removeClass('is-valid');
    
    let url = $('#target_url').val();
    if (urlRegex.test(url)) {
        $('#target_url').addClass('is-valid');
        return true;
    } else {
        $('#target_url').addClass('is-invalid');
        return false;
    }
};

const validate_campaign_name = function () {
    $('#campaign_name').removeClass('is-invalid');
    $('#campaign_name').removeClass('is-valid');

    let campaign_name = $('#campaign_name').val();
    if (campaign_name == '') {
        $('#campaign_name').addClass('is-invalid');
        return false;
    } else {
        if (companyNameRegex.test(campaign_name)) {
            $('#campaign_name').addClass('is-valid');
            return true;
        } else {
            $('#campaign_name').addClass('is-invalid');
            return false;
        }
    }
};

const check_adv = function () {
    is_adv = !is_adv;
};

const decs_manage = function (focus_id) {
    $('#desc_product_type').hide();
    $('#desc_page_type').hide();
    $('#desc_medium').hide();
    $('#desc_source').hide();
    $('#desc_campaign').hide();
    $('#desc_content').hide();
    $('#desc_project').hide();
    $('#desc_campaign_name').hide();
    $(`#desc_${focus_id}`).show();
}

const set_start_value = function (api_url) {
    $.ajax({
        url: api_url,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            _info = data;
            for (let user of data.users) {
                if (user.is_bot){
                    continue;
                }
                $('#user').append(new Option(user.value, user.ident));
            }
            for (let product_type of data.term_materials) {
                $('#product_type').append(new Option(product_type.value, product_type.ident));
            }
            for (let page_type of data.term_pages) {
                $('#page_type').append(new Option(page_type.value, page_type.ident));
            }
            for (let medium of data.mediums) {
                $('#medium').append(new Option(medium.value, medium.ident));
            }
            for (let content of data.contents) {
                $('#content').append(new Option(content.value, content.ident));
            }
            for (let prj of data.campaign_projects) {
                $('#project').append(new Option(prj.value, prj.ident));
            }
            update_source();
            refresh_table();

        },
        error: function (data) {
            console.log(data);
        }
    });
};

const update_source = function () {
    let source = $('#source');
    let id_medium = $('#medium').val();
    source.empty();
    for (let medium of _info.mediums) {
        if (medium.ident == id_medium) {
            for (let source_item of medium.sources) {
                source.append(new Option(source_item.value, source_item.ident));
            }
        }
    }
};

const refresh_table = function () {
    $.ajax({
        url: _url_last_10_utms,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            $('#table_body').empty();
            for (let utm of data.links) {
                let _date = new Date(utm.campaign_date);
                let _str_date = _date.toLocaleDateString('en-GB', {
                    day: 'numeric', month: 'short', year: 'numeric'
                });
                $('#table_body').append(`<tr>
                    <td>${_str_date}</td>
                    <td>${utm.user_name}</td>
                    <td><a href="${utm.full_url}" target="_blank">${utm.full_url}</a></td>
                </tr>`);
            }
        },
        error: function (data) {
            console.log(data);
        }
    });
}

const get_utm = function () {
    $('#result_url').val('');
    if (!validate_url()) {
        $('#done_link').modal('hide');
        return;
    }
    if (is_adv && !validate_campaign_name()) {
        $('#done_link').modal('hide');
        return;
    }
    var create_link_form = new FormData();
    create_link_form.append('target_url', $('#target_url').val());
    create_link_form.append('user', $('#user').val());
    create_link_form.append('term_material', $('#product_type').val());
    create_link_form.append('source', $('#source').val());
    create_link_form.append('medium', $('#medium').val());
    create_link_form.append('campaign_project', $('#project').val());
    create_link_form.append('term_page', $('#page_type').val());

    if (is_adv) {
        create_link_form.append('campaning_dop', $('#campaign_name').val());
        create_link_form.append('content', $('#content').val());
    }

    $.ajax({
        url: _url_get_utm,
        type: 'POST',
        data: create_link_form,
        processData: false,
        contentType: false,
        dataType: 'json',
        success: function (data) {
            $('#result_url').val(data.full_url);
            refresh_table();
        },
        error: function (data) {
            console.log(data);
        }
    });
}

const copyToClipboard = function (){
    navigator.clipboard.writeText($('#result_url').val());
}
