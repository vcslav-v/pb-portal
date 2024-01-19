const per_page = 30;

var disable_cards = [];
var all_products = [];
var page_products = [];
var cur_category_name;
var cur_category_id;
var _page = 1;
var _img_url = '';
var _page_html_url = '';
var _add_tag_url = '';
var _search_tag_url = '';
var _main_site_url = '';
var _refresh_active_tasks_url = '';
var _imgs = JSON.parse(localStorage.getItem('_imgs')) || {};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

const darkenCard = function (event) {
    var card = event.currentTarget.closest('.card');
    if (disable_cards.includes(cardId)) {
        return;
    }
    var cardId = card.getAttribute('data-card-id'); // ID кнопки
    disable_cards.push(cardId);
    console.log('Card ID: ' + cardId); // Логируем ID

    // Добавляем затемнение
    card.style.position = 'relative';
    card.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    card.style.color = 'white';


    // Добавляем кнопку "return"
    const returnButton = document.createElement('button');
    returnButton.innerText = 'Return';
    returnButton.className = 'btn btn-primary position-absolute top-50 start-50 translate-middle';

    returnButton.onclick = function () {
        // Возвращаем исходное состояние карточки
        card.style.backgroundColor = '';
        card.style.color = '';
        returnButton.remove();
        disable_cards.splice(disable_cards.indexOf(cardId), 1);

    };
    card.appendChild(returnButton);
}

const show_page = function () {
    var startIndex = (_page - 1) * per_page;
    var endIndex = _page * per_page;
    page_products = all_products.slice(startIndex, endIndex);
    var formData = new FormData();
    formData.append('products', JSON.stringify(page_products));
    formData.append('category_name', cur_category_name);
    $.ajax({
        type: 'POST',
        url: _page_html_url,
        data: formData,
        dataType: 'html',
        contentType: false,
        cache: false,
        mimeType: "multipart/form-data",
        processData: false,
        success: function (response) {
            var page = $('#products_list');
            page.empty();
            page.append(response);
            document.querySelectorAll('.btn-close').forEach(function (button) {
                button.addEventListener('click', darkenCard);
            });
            for (var i = 0; i < disable_cards.length; i++) {
                card = document.querySelector('[data-card-id="' + disable_cards[i] + '"]');
                if (!card) {
                    continue;
                }
                cardId = card.getAttribute('data-card-id'); // ID кнопки
                card.style.position = 'relative';
                card.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                card.style.color = 'white';


                // Добавляем кнопку "return"
                const returnButton = document.createElement('button');
                returnButton.innerText = 'Return';
                returnButton.className = 'btn btn-primary position-absolute top-50 start-50 translate-middle';

                returnButton.onclick = function () {
                    // Возвращаем исходное состояние карточки
                    card.style.backgroundColor = '';
                    card.style.color = '';
                    returnButton.remove();
                    disable_cards.splice(disable_cards.indexOf(cardId), 1);
                }
                card.appendChild(returnButton);
            }
            if (all_products.length <= per_page) {
                $('#pagination_block').hide();
            } else {
                $('#pagination_block').show();
                if (_page == 1) {
                    $('#prev_button').addClass('disabled');
                } else {
                    $('#prev_button').removeClass('disabled');
                }
                if (_page * per_page >= all_products.length) {
                    $('#next_button').addClass('disabled');
                } else {
                    $('#next_button').removeClass('disabled');
                }
            }
            show_imgs();
        },
        error: function (error) {
            console.log(error);
        },
    });


}

const show_imgs = function () {
    $('img[name="product_img"]').each(function () {
        var cardId = $(this).closest('div').attr('data-card-id');
        if (_imgs[cardId]) {
            $(this).attr('src', _imgs[cardId]);
        }
    });
};

const load_imgs = function () {
    for (var i = 0; i < all_products.length; i++) {
        if (_imgs[all_products[i].id]) {
            continue;
        }
        var formData = new FormData();
        formData.append(
            'products', JSON.stringify([all_products[i]]),
        );
        $.ajax({
            type: 'POST',
            url: _img_url,
            data: formData,
            dataType: 'json',
            contentType: false,
            cache: false,
            mimeType: "multipart/form-data",
            processData: false,
            success: function (response) {
                _imgs = Object.assign(_imgs, response);
                localStorage.setItem('_imgs', JSON.stringify(_imgs));
                show_imgs();
            },
            error: function (error) {
                console.log(error);
            },
        });
    }
};

const changepage = function (delta) {
    if (_page + delta < 1 || _page + delta > Math.ceil(all_products.length / per_page)) {
        return;
    }
    _page += delta;
    show_page();
};

const set_search = function (url, page_html_url, img_url, add_tag_url, refresh_active_tasks_url, search_tag_url, main_site_url) {
    var search_form = document.getElementById('search_form');
    var tag_input = document.getElementById('tag_input');
    $('#load_spin').hide();
    _add_tag_url = add_tag_url;
    _refresh_active_tasks_url = refresh_active_tasks_url;
    _search_tag_url = search_tag_url;
    _main_site_url = main_site_url;
    refresh_active_tasks();
    search_form.onsubmit = function (e) {
        e.preventDefault();
        var page = $('#products_list');
        page.empty();
        $('#load_spin').show();
        
        var formData = new FormData(search_form);
        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            dataType: 'json',
            contentType: false,
            cache: false,
            mimeType: "multipart/form-data",
            processData: false,
            success: function (response) {
                $('#pagination_block').hide();
                disable_cards = [];
                all_products = response.products;
                _page = 1;
                _img_url = img_url;
                _page_html_url = page_html_url;
                cur_category_name = response.category_name;
                cur_category_id = response.category_id;
                $('#load_spin').hide();
                show_page()
                load_imgs();
            },

            error: function (error) {
                console.log(error);
            },
        });
    }
    tag_input.onchange = function (e) {
        build_tag_url(e);
    }
};

const add_tag = function () {
    console.log('add_tag');
    $('#confirmModal').modal('hide');
    $('<div id="overlay"></div>').appendTo(document.body);
    var formData = new FormData();
    formData.append(
        'products', JSON.stringify(all_products),
    );
    formData.append('category_id', cur_category_id);
    formData.append('disable_cards', JSON.stringify(disable_cards));
    formData.append('tag', $('input[name="tag"]').val());
    $.ajax({
        type: 'POST',
        url: _add_tag_url,
        data: formData,
        dataType: 'json',
        contentType: false,
        cache: false,
        mimeType: "multipart/form-data",
        processData: false,
        success: function (response) {
            $('#overlay').remove();
            $('#resultBody').text(response.message);
            $('#resultModal').modal('show');
            $('input[name="tag"]').val('');
            refresh_active_tasks();
        },
        error: function (error) {
            $('#overlay').remove();
            $('#resultBody').text(response.message);
            $('#resultModal').modal('show');
        },
    });

};

const refresh_confirm_message = function () {
    $('#modal_loader').show();
    $('#confirmation_text').hide();

    var formData = new FormData();
    formData.append(
        'tag', $('input[name="tag"]').val(),
    );
    $.ajax({
        type: 'POST',
        url: _search_tag_url,
        data: formData,
        dataType: 'json',
        contentType: false,
        cache: false,
        mimeType: "multipart/form-data",
        processData: false,
        success: function (response) {
            var count = all_products.length - disable_cards.length;
            $('#modal_loader').hide();
            if (response.name != undefined) {
                var message = 'Tag "' + $('input[name="tag"]').val() + '" already exists. Add it to ' + count + ' products?';
            } else {
                var message = 'Create tag "' + $('input[name="tag"]').val() + '" and assign it to ' + count + ' products?';
            }
            $('#confirmation_text').empty();
            $('#confirmation_text').text(message);
            $('#confirmation_text').show();
        },
        error: function (error) {
            alert(error);
        },
    });
};

const refresh_active_tasks = function () {
    $.ajax({
        type: 'GET',
        url: _refresh_active_tasks_url,
        dataType: 'json',
        contentType: false,
        cache: false,
        mimeType: "multipart/form-data",
        processData: false,
        success: function (response) {
            $('#active_task').empty();
            $('#active_task').append(response.count);
        },

        error: function (error) {
            console.log(error);
        },
    });
};

const build_tag_url = function (e) {
    var tag = e.target.value;
    tag = tag.replace(/\s/g, "+");
    var url = _main_site_url + '/search?text=' + tag;
    $('#tag_url').text(url);
    $('#tag_url').attr('href', url);
};
