// Handle user input and fetch city suggestions via AJAX
const cityInput = document.getElementById("city");
const suggestionsBox = document.getElementById("suggestions");
const hotelListContainer = document.getElementById("hotel-list");

cityInput.addEventListener("input", function() {
    const query = cityInput.value.trim();

    if (query.length >= 1) {  // Start searching after at least 1 character
        $.ajax({
            url: "{% url 'city_autocomplete' %}",
            data: {
                'q': query  // Send user input as a query parameter
            },
            success: function(data) {
                displaySuggestions(data);  // Display the city suggestions
            }
        });
    } else {
        suggestionsBox.innerHTML = '';  // Clear suggestions if input is empty
    }
});

// Display the city suggestions below the input field
function displaySuggestions(cities) {
    suggestionsBox.innerHTML = '';  // Clear previous suggestions

    if (cities.length === 0) {
        suggestionsBox.innerHTML = '<div>No cities found</div>';
        return;
    }

    cities.forEach(function(city) {
        const div = document.createElement("div");
        div.textContent = city.name;
        div.onclick = function() {
            cityInput.value = city.name;  // Set the selected city name in the input
            fetchHotels(city.id);  // Fetch hotels for the selected city
            suggestionsBox.innerHTML = '';  // Clear suggestions after selection
        };
        suggestionsBox.appendChild(div);
    });
}

// Fetch hotels for the selected city via AJAX
function fetchHotels(cityId) {
    $.ajax({
        url: `/hotels/${cityId}/`,
        success: function(data) {
            if (data.hotels && data.hotels.length > 0) {
                displayHotels(data.hotels);
            } else {
                hotelListContainer.innerHTML = "<p>No hotels found in this city.</p>";
            }
        },
        error: function() {
            hotelListContainer.innerHTML = "<p>There was an error fetching hotels.</p>";
        }
    });
}

// Display hotels on the page
function displayHotels(hotels) {
    let hotelListHtml = '<h2>Hotels</h2><ul>';
    hotels.forEach(function(hotel) {
        hotelListHtml += `<li>${hotel.name} (Code: ${hotel.code})</li>`;
    });
    hotelListHtml += '</ul>';
    hotelListContainer.innerHTML = hotelListHtml;
}
