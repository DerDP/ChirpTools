const popupOverlay = document.querySelector(".popup-overlay");
const popupContainer = document.querySelector(".popup-container");
const closePopupButton = document.getElementById("close-popup");
const active = document.getElementsByClassName("ant-menu-item");

$( document ).ready(function() {
    active[0].className = "ant-menu-item"
    active[1].className = "ant-menu-item ant-menu-item-selected"
});

function openPopup() {
    popupOverlay.style.display = "flex";
    setTimeout(() => {
        popupContainer.style.opacity = "1";
        popupContainer.style.transform = "scale(1)";
    }, 100);
}

function closePopup() {
    popupContainer.style.opacity = "0";
    popupContainer.style.transform = "scale(0.8)";
    setTimeout(() => {
        popupOverlay.style.display = "none";
    }, 300);
}


closePopupButton.addEventListener("click", closePopup);


function checkRegex(pattern, type, divId) {

    const textField = document.getElementById(divId);
    const lines = textField.value.split('\n');
    let validLines = [];

    document.getElementById("line_issue").innerHTML = ""
    lines.forEach((line, index) => {
        if (pattern.test(line.trim()) || line.trim() === "") {

            validLines.push(line);

        }
        if (!pattern.test(line.trim()) && line != "") {
            document.getElementById("line_issue").innerHTML += `Value <b>'${line}'</b> is not valid ${type} and it was removed!`
            openPopup();
        }
    });

    textField.value = validLines.join('\n');

}

$("#EUI_Text").change(function () {
    checkRegex(/^(?:[A-Fa-f0-9]{2}){8}$|^0x([A-Fa-f0-9]{2},\s?){7}[A-Fa-f0-9]{2}$/, 'EUI', 'EUI_Text')
});
$("#AppID_Text").change(function () {
    checkRegex(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89aAbB][0-9a-f]{3}-[0-9a-f]{12}$/i, 'AppID', 'AppID_Text')
});
$("#ProfileID_Text").change(function () {
    checkRegex(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89aAbB][0-9a-f]{3}-[0-9a-f]{12}$/i, 'ProfileID', 'ProfileID_Text')
});
$("#AppKey_Text").change(function () {
    checkRegex(/^[0-9a-fA-F]{32}$/, 'AppKey', 'AppKey_Text')
});