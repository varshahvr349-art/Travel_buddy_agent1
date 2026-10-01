const form = document.getElementById("travelForm");

const searchButton = document.getElementById("searchButton");
const buttonText = document.getElementById("buttonText");
const loader = document.getElementById("loader");

const aiResponse = document.getElementById("aiResponse");


form.addEventListener("submit", function (event) {

    event.preventDefault();

    // Get values from form
    const source = document.getElementById("origin").value;
    const destination = document.getElementById("destination").value;
    const travelDate = document.getElementById("date").value;

    // Get selected time
    const timeElement = document.getElementById("time");

    const travelTime = timeElement
        ? timeElement.value
        : "any";


    // Show loading
    searchButton.disabled = true;

    buttonText.textContent = "Planning...";

    loader.style.display = "inline-block";

    aiResponse.textContent =
        "🤖 TravelBuddy is planning your trip...\n\n" +
        "Searching attractions and flights...";


    // Send request to Flask
    fetch("http://127.0.0.1:5000/travel", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            source: source,

            destination: destination,

            travel_date: travelDate,

            travel_time: travelTime

        })

    })

    // Convert Flask response to JSON
    .then(function (response) {

        if (!response.ok) {

            throw new Error(
                "Server error: " + response.status
            );

        }

        return response.json();

    })

    // Display AI response
    .then(function (data) {

        console.log("Response from Flask:");
        console.log(data);

        console.log("AI Response:");
        console.log(data.response);


        // THIS displays the response in the UI
        aiResponse.textContent = data.response;


        // Scroll to AI result
        document.getElementById("aiResult")
            .scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

    })

    // Handle error
    .catch(function (error) {

        console.error("Error:", error);

        aiResponse.textContent =
            "❌ Something went wrong.\n\n" +
            error.message;

    })

    // Always execute
    .finally(function () {

        searchButton.disabled = false;

        buttonText.textContent =
            "🔍 Search Trip";

        loader.style.display = "none";

    });

});