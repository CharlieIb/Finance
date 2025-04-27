function showInputs() {
    var oldpassword = document.getElementById("oldpassword");
    var password1 = document.getElementById("password1");
    var password2 = document.getElementById("password2");

    document.getElementById("changepassword").style.display = "None";

    oldpassword.classList.remove("input-hidden");
    oldpassword.classList.add("input-visible");
    password1.classList.remove("input-hidden");
    password1.classList.add("input-visible");
    password2.classList.remove("input-hidden");
    password2.classList.add("input-visible");
    changepassword2.classList.remove("input-hidden");
    changepassword2.classList.add("input-visible");
}

function showInputs2() {
    var add_amount = document.getElementById("add_amount");
    var add_cash_confirm = document.getElementById("add_cash_confirm");

    document.getElementById("add_cash").style.display = "None";

    add_amount.classList.remove("input-hidden");
    add_amount.classList.add("input-visible");
    add_cash_confirm.classList.remove("input-hidden");
    add_cash_confirm.classList.add("input-visible");
}

function showBalance() {
    var balanceBox = document.getElementById("balance-box");
    if (balanceBox.style.visibility === "hidden") {
        balanceBox.style.visibility = "visible";
    } else {
        balanceBox.style.visibility = "hidden";
    }
}