// ADD UPLOAD PROCESSS
const loadingOverlay = document.getElementById("loadingOverlay");
const submit = document.getElementById("submit");
const loading = document.getElementById("loading");

$(document).ready(function() {

    $('#uploadForm').on('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission

        var formData = new FormData(this); // Gather all form data, including additional fields
        loadingOverlay.classList.remove("hidden")
        loadingOverlay.classList.add("flex")

        $.ajax({
            url: "/pmbp/report/create/", // URL to your view
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                // Update progress bar during upload
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100;
                        $('#progressBar').val(percentComplete);
                        $('#progressPercentage').text(Math.round(percentComplete) + '%');
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                location.assign("/pmbp/report")
            },
            error: function() {
                alert('Gagal upload gambar!.');
                location.reload()
            }
        });
    });
});


document.addEventListener("pageShow", ()=>{
    submit.classList.remove("hidden");
    loadingOverlay.classList.add("hidden");
    loadingOverlay.classList.remove("flex");
    loading.classList.add("hidden");
  })