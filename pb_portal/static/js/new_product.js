htmx.onLoad(function (content) {
  var sortables = content.querySelectorAll(".sortable");
  for (var i = 0; i < sortables.length; i++) {
    var sortable = sortables[i];
    var sortableInstance = new Sortable(sortable, {
      animation: 150,
      ghostClass: 'blue-background-class',

      // Make the `.htmx-indicator` unsortable
      filter: ".htmx-indicator",
      onMove: function (evt) {
        return evt.related.className.indexOf('htmx-indicator') === -1;
      },

      //   // Disable sorting on the `end` event
      //   onEnd: function (evt) {
      //     this.option("disabled", true);
      //   }
    });

    // Re-enable sorting on the `htmx:afterSwap` event
    sortable.addEventListener("htmx:afterSwap", function () {
      sortableInstance.option("disabled", false);
    });
  }
  var simplemde = new SimpleMDE({
    element: document.getElementById("description"),
    spellChecker: false,
    status: false,
    toolbar: false,
    renderingConfig: {
      singleLineBreaks: true,
    },
    autofocus: false,
    initialValue: '',
  });
  document.querySelector(".CodeMirror").classList.add("border", "rounded-md", "py-2", "px-4", "focus:outline-none", "mt-2");
})

async function startUpload() {
  let formData = new FormData();
  let uploadSessionId = document.getElementsByName('upload_session_id')[0].value;
  formData.append('upload_session_id', uploadSessionId);
  const requestOptions = {
    method: 'POST',
    body: formData
  };
  const response = fetch('/products/get_upload_product_url', requestOptions);
  const data = await response
  const uploadUrl = data.json().url;

  let s3FormData = new FormData();
  let file = document.getElementsByName('productFile').files[0];
  s3FormData.append('file', file);
  htmx.ajax('POST', uploadUrl, {
    body: formData,
    headers: { 'HX-Request': 'true' },
    responseType: 'json',
    onprogress: function(event) {
        if (event.lengthComputable) {
            var percentComplete = (event.loaded / event.total) * 100;
            console.log(percentComplete);
        }
    }
});


}

