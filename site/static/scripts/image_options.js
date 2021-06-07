
function image_download(ip,id,img_name,type)
{
    window.open('/uploads/' + ip + "," + id + '/' + img_name + '/'+type)
}


function image_delete(ip,id,img_name,type)
{
    let arrStr = encodeURIComponent(JSON.stringify(img_name));
    if (type === "webcam") {
        window.open('/delete/' + ip + "," + id + '?webcams=' + arrStr)
    }
    else{
        window.open('/delete/' + ip + "," + id + '?images=' + arrStr)
    }
        back()
}


function back(ip,id)
{
    window.open('/clients/' + ip + "," + id)
}