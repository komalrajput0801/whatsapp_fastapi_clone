$(document).ready(function() {
    const loginContainer = $('#login-container');
    const registerContainer = $('#register-container');

    // Initially display the login form
    loginContainer.addClass('active');

    // Toggle between login and register forms
    function toggleForms() {
        if (loginContainer.hasClass('active')) {
            loginContainer.removeClass('active');
            registerContainer.addClass('active');
        } else {
            registerContainer.removeClass('active');
            loginContainer.addClass('active');
        }
    }

    $('#show-register-form').click(function(e) {
        e.preventDefault();
        toggleForms();
    });

    $('#show-login-form').click(function(e) {
        e.preventDefault();
        toggleForms();
    });

    // Mock login and register functionality
    $('#login-form').submit(async function(e) {
        e.preventDefault();
        try{
            const formDataArray = $(this).serializeArray();

            // Convert the serialized array to a JSON object
            const formData = {};
            formDataArray.forEach(item => {
                formData[item.name] = item.value;
            });
            formData["grant_type"] = ""
            formData["scope"] = ""
            formData["client_id"] = ""
            formData["client_secret"] = ""

            const response = await fetch("/login/", {
                method: "POST",
                body: $(this).serialize() + "&grant_type=&scope=&client_id=&client_secret=",
                headers: { 
                    "Content-type": "application/x-www-form-urlencoded"
                }
            });
            if(!response.ok){
                console.log("Error occurred when logging data::", response)
                const json = await response.json();
                alert(json.detail);
            }
            else{
                console.log(response);
                const json = await response.json();
                console.log(json);
                if(json.access_token){
                    localStorage.setItem("token", json.access_token);
                    localStorage.setItem("senderId", json.senderId);
                }
                loginContainer.removeClass('active');
                alert('Logged in successfully!');
                window.location.href = "/chats/";
            }
        }
        catch(error){
            console.error("Error ocurred when logging in ..........", error)
        }
    });

    $('#register-form').submit(async function(e) {
        e.preventDefault();
        try{
            const formDataArray = $(this).serializeArray();

            // Convert the serialized array to a JSON object
            const formData = {};
            formDataArray.forEach(item => {
                formData[item.name] = item.value;
            });
            const response = await fetch("/register/", {
                method: "POST",
                body: JSON.stringify(formData),
                headers: { 
                    "Content-type": "application/json; charset=UTF-8"
                }
            });
            if(!response.ok){
                console.log("Error occurred when registering data::", response)
            }
            else{
                console.log(response);
            }
        } catch(error){
            console.error("Error occurred when registering data.........")
        }
        
        registerContainer.removeClass('active');
        alert('Registered successfully!');
        loginContainer.addClass("active");
    });
});
