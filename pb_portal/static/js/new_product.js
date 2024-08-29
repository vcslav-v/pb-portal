let currentUploadRequest = null;
let simplemde = null;
let sortableInstance = null;

document.addEventListener("DOMContentLoaded", function () {
  let sortables = document.querySelectorAll(".sortable");
  for (var i = 0; i < sortables.length; i++) {
    var sortable = sortables[i];
    sortableInstance = new Sortable(sortable, {
      animation: 150,
      ghostClass: 'blue-background-class',
      filter: ".htmx-indicator",
      onMove: function (evt) {
        return evt.related.className.indexOf('htmx-indicator') === -1;
      },
    });
    sortable.addEventListener("htmx:afterSwap", function () {
      sortableInstance.option("disabled", false);
    });
  }

  simplemde = new SimpleMDE({
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
  simplemde.codemirror.on("change", function () {
    syncText();
  });
})

document.body.addEventListener('htmx:afterRequest', function (event) {
  if (event.detail.target.classList.contains('preview-img-block')) {
    let sortedPreview = document.getElementById('sortedPreview');
    let hasnotPreviewBlocks = sortedPreview.querySelectorAll('.preview-img-block').length == 0;
    if (hasnotPreviewBlocks) {
      sortedPreview.classList.add('hidden');
    };
  } else if (event.target.id == 'addYoutubeBtn') {
    let youtubeInput = document.getElementById('youtubeLink');
    youtubeInput.value = '';
  }
});

function showSortedPreview() {
  var sortedPreview = document.getElementById("sortedPreview");
  if (sortedPreview) {
    sortedPreview.classList.remove("hidden");
  }
};

function startUpload() {
  let formData = new FormData();
  let uploadSessionId = document.getElementsByName('upload_session_id')[0].value;
  formData.append('upload_session_id', uploadSessionId);
  const xhr = new XMLHttpRequest();
  let file = document.getElementById('productFile').files[0];
  if (file && file.size > 4 * 1024 * 1024 * 1024) {
    alert('File is too big. Maximum size is 4GB.');
    return;
  }
  if (file) {
    xhr.open('POST', "/products/get_upload_product_url");
    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          uploadFile(file, response.data);
        }
        else {
          alert('Could not get signed URL.');
        }
      }
    };
    xhr.send(formData);
  }
}

function uploadFile(file, s3Data) {
  const xhr = new XMLHttpRequest();
  currentUploadRequest = xhr;
  const productBar = document.getElementById('productBar');
  let productProgress = document.getElementById('productProgress');
  let productName = document.getElementById('productName');
  let uploadBtn = document.getElementById('uploadBtn');
  productName.textContent = file.name;
  productBar.classList.remove('hidden');
  uploadBtn.classList.add('hidden');
  xhr.open('POST', s3Data.url);
  xhr.setRequestHeader('x-amz-acl', 'public-read');
  const postData = new FormData();
  for (key in s3Data.fields) {
    postData.append(key, s3Data.fields[key]);
  }
  postData.append('file', file);
  xhr.upload.onprogress = (event) => {
    if (event.lengthComputable) {
      const percentComplete = (event.loaded / event.total) * 100;
      productProgress.style.width = (100 - percentComplete) + '%';
    }
  };
  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4) {
      if (xhr.status === 200 || xhr.status === 204) {
        currentUploadRequest = null;
        console.log('File uploaded successfully.');
      }
      else if (xhr.status === 0) {
        console.log('File upload cancelled.');
      }
      else {
        alert('Could not upload file.');
      }
    }
  };
  xhr.send(postData);
}

function cancelUpload() {
  let uploadBtn = document.getElementById('uploadBtn');
  let productBar = document.getElementById('productBar');
  let productProgress = document.getElementById('productProgress');
  let fileInput = document.getElementById('productFile');
  if (currentUploadRequest) {
    currentUploadRequest.abort();
    productBar.classList.add('hidden');
    uploadBtn.classList.remove('hidden');
    productProgress.style.width = '100%';
  } else {
    let formData = new FormData();
    let uploadSessionId = document.getElementsByName('upload_session_id')[0].value;
    formData.append('upload_session_id', uploadSessionId);
    const xhr = new XMLHttpRequest();
    xhr.open('POST', "/products/rm_upload_product_url");
    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          productBar.classList.add('hidden');
          uploadBtn.classList.remove('hidden');
          productProgress.style.width = '100%';
          fileInput.value = '';
          console.log('Upload session removed.');
        }
        else {
          alert('Could not remove product.');
        }
      }
    };
    xhr.send(formData);
  }
}

function syncText() {
  let textarea = document.getElementById('description');
  let html_description = simplemde.value();
  textarea.value = simplemde.markdown(html_description);
  htmx.trigger(textarea, 'change');
}

function deleteTag(tag) {
  let tagsArea = document.getElementById('tags');
  let tagName = tag.getAttribute('x-value')
  let tags = tagsArea.value.split(',').map(tag => tag.trim());
  tags = tags.filter(t => t.toLowerCase() !== tagName);
  tagsArea.value = tags.join(', ');
  htmx.trigger(tagsArea, 'input');
}
