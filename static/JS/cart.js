


$(document).ready(function() {
    console.log("Howdy")

    var add_buttons = document.getElementsByClassName("add_this")

    for (i = 0; i < add_buttons.length; i++) {
        console.log("checking", i)
        add_buttons[i].addEventListener('click', function() {
            var item_id = parseInt(this.dataset.product)
            var action = this.dataset.action
            console.log("Item is", item_id, "and we want to", action)

            console.log("USER:", user)
            if (user === 'AnonymousUser') {
                console.log("not authenticated")
            } else {
                updateUserOrder(item_id, action)
            }
        })
    }

    function updateUserOrder(item_id, action) {
        console.log("wahoo!")
        var url = "/update_cart/"

        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X_CSRFToken": csrftoken
            },
            body: JSON.stringify({
                "item_id": item_id,
                "action": action
            })
        })

        .then((response) => {
            console.log('Response:', response)
            return response.json()
        })
        .then((response) => {
            console.log("data:", data)
        })
    }
})