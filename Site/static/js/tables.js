$(document).ready(function () {

    (function ($) {

        $('#tableSearch').keyup(function () {

            var rex = new RegExp($(this).val(), 'i');
            $('.searchable tr').hide();
            $('.searchable tr').filter(function () {
                return rex.test($(this).text());
            }).show();

        })

    }(jQuery));

});

$('td[data-href]').on("click", function() {
    document.location = $(this).data('href');
});