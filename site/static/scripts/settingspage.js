function isIdentical() {
    var password1 = document.getElementById("newPassword");
    var password2 = document.getElementById("retypePassword");
    error = document.getElementById("errorRetype");

    if ((password1.value.length > 0) && (password2.value.length > 0)) {
        if (password1.value === password2.value) {
            error.style.display = "none";
            return true
        } else if (error.style.display === "none") {
            error.style.display = "block";
            return false
        }
    } else {
        error.style.display = "none";
    }

}

function validateEmail() {
    let email = document.getElementById('newEmail').value
    let error = document.getElementById("EmailError")
    console.log(email)
    var re = /\S+@\S+\.\S+/;
    if(! re.test(email) && email.length >0){
        error.style.display = 'block'
    }
    else{
        error.style.display = 'none'
    }
    return re.test(email)
}


function isLongerThanMin() {
    const newPass = document.getElementById("newPassword");
    const lengthError = document.getElementById("errorLength")
    if ((newPass.value.length < 8) && (newPass.value.length > 0)) {
        lengthError.style.display = "block"
        return false
    } else if (newPass.value.length === 0) {
        lengthError.style.display = "none"
        return false
    } else {
        lengthError.style.display = "none"
        return true
    }


}

function checkValid() {
    isIdentical()
    isLongerThanMin()

}

function confirmChanges() {
    var passError = document.getElementById("errorRetype")
    var password1 = document.getElementById("newPassword")
    var password2 = document.getElementById("retypePassword")
    var email = document.getElementById("newEmail")
    if (document.getElementById("confirm").value.length === 0) {
        document.getElementById("confirmError").style.display = "block"
        return
    }
    else{
        document.getElementById("confirmError").style.display = "none"
    }


    if (isLongerThanMin()) {
        if (isIdentical()) {
            let form = document.getElementById("form");
            form.submit()
        }
    } else if (validateEmail()) {
        let form = document.getElementById("form");
        form.submit()
    }
}

function closePopUp() {
    var popUp = document.getElementById("popUp");
    popUp.style.display = "none";

}

function closeError(id) {
    let error = document.getElementById(id)

    if (error !== null && error.style.display === 'block') {
        error.style.display = 'none';
    } else if (error !== null && error.classList.contains('invalid-feedback')) {

        error.style.display = 'none';
    }
}
