// Call the dataTables jQuery plugin
// $(document).ready(function() {
//   $('#dataTable').DataTable();
// });

$(document).ready(function () {
    var table = $('#dataTable').DataTable({
        "columnDefs": [{
            "targets": -1,
            "data": null,
            "defaultContent": "<button href=\"#\" class=\"btn btn-danger btn-icon-split\">\n" +
                "                    <span class=\"icon text-white-50\">\n" +
                "                      <i class=\"fas fa-trash\"></i>\n" +
                "                    </span>\n" +
                "                    <span class=\"text\">Remove</span>\n" +
                "                  </button>"
        }]
    });

    $('#dataTable tbody').on('click', 'button', function () {
        var data = table.row($(this).parents('tr')).data();
        if (data[4] !== data[5]) {
            $("#warningModal").modal()
        } else {
            url_ = "http://10.132.57.216:8080/delete-book/<" + data[0] + ">"
            $.ajax({
                type: "POST",
                dataType: "json",
                url: url_,
		success: function (result) {
            		window.location.replace("10.132.57.216:8080/");
		}
            });
        }
    });
});
