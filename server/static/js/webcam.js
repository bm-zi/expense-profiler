function takePhoto(photo, canvas, video, width, height) {
  const ctx = canvas.getContext("2d");
  canvas.width = width;
  canvas.height = height;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const data = canvas.toDataURL("image/png");
  photo.setAttribute("src", data);

  canvas.toBlob(function (blob) {
    const file = new File([blob], "receipt.png", { type: "image/png" });
    let container = new DataTransfer();
    container.items.add(file);
    const imageUploader = document.getElementById("id_receipt_image");
    imageUploader.files = container.files;
  }, "image/png");

  document.getElementById("photo").style.display = "flex";
}

// function activateBtn(button) {
//   if (!button.classList.contains("active")) {
//     button.classList.add("active");
//   }
// }

// function deactivateBtn(button) {
//   if (button.classList.contains("active")) {
//     button.classList.remove("active");
//   }
// }

function addListenersToMethodChoosers() {
  const setTakePhotoBtn = document.getElementById(
    "select-take-photo-method-btn"
  );
  const setUploadPhotoBtn = document.getElementById(
    "select-upload-photo-method-btn"
  );

  const takePhotoContainer = document.getElementById("take-photo-container");
  const uploadPhotoContainer = document.getElementById(
    "upload-photo-container"
  );

  setTakePhotoBtn.addEventListener("click", () => {
    takePhotoContainer.style.display = "flex";
    uploadPhotoContainer.style.display = "none";

    // setUploadPhotoBtn.style.display = "block";
    // this.style.display = "none";
  });
  setUploadPhotoBtn.addEventListener("click", () => {
    takePhotoContainer.style.display = "none";
    uploadPhotoContainer.style.display = "flex";

    // setUploadPhotoBtn.style.display = "none";
    // this.style.display = "block";
  });
}

function addListenerToUploadInput() {
  const imageUploader = document.getElementById("id_receipt_image");
  const uploadedPhoto = document.getElementById("uploaded-photo");
  imageUploader.addEventListener("change", () => {
    if (imageUploader.files && imageUploader.files[0]) {
      let reader = new FileReader();
      reader.onload = function (e) {
        uploadedPhoto.setAttribute("src", e.target.result);
        uploadedPhoto.style.display = "block";
      };
      reader.readAsDataURL(imageUploader.files[0]);
    } else {
      uploadedPhoto.style.display = "none";
    }
  });
}

(main = async () => {
  const video = document.getElementById("webcam");
  const photo = document.getElementById("photo");
  const canvas = document.getElementById("canvas");
  const takePhotoButton = document.getElementById("take-photo-button");
  const videoSize = { width: 1920, height: 1080 };
  const videoConstraints = {
    audio: false,
    video: videoSize,
  };
  let stream = null;
  photo.style.display = "None";
  try {
    stream = await navigator.mediaDevices.getUserMedia(videoConstraints);
  } catch (err) {
    console.error(`${err.name}: ${err.message}`);
    return null;
  }
  video.srcObject = stream;
  video.onloadedmetadata = () => {
    video.play();
  };
  takePhotoButton.addEventListener(
    "click",
    (e) => {
      e.preventDefault();
      takePhoto(photo, canvas, video, videoSize.width, videoSize.height);
    },
    false
  );

  addListenersToMethodChoosers();
  addListenerToUploadInput();
})();
