document.addEventListener("DOMContentLoaded", function () {
  var startCalibrationButton = document.getElementById("startCalibration");
  var buttons = document.querySelectorAll("button");
  var recommendedList = document.getElementById("recommended-list");

  var previousElement = null;
  var consecutiveMatches = 0;

  function isValidCoordinate(coord) {
    return typeof coord === "number" && isFinite(coord);
  }

  function getElementFromPoint(x, y) {
    if (!isValidCoordinate(x) || !isValidCoordinate(y)) {
      return null;
    }
    return document.elementFromPoint(x, y);
  }

  function handleClick(button) {
    if (button) {
      console.log("Button clicked:", button.textContent);
    }
  }

  function simulateButtonClick(button) {
    if (button) {
      console.log("Simulating click on:", button.textContent);
      var movieName = button.textContent;
      var payload = { movie_name: movieName };
      fetch("http://192.168.1.6:8888/recommend", {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          console.log("Recommendation API response:", data);

          if (
            data &&
            data.recommended_movies &&
            Array.isArray(data.recommended_movies)
          ) {
            recommendedList.innerHTML = "";

            data.recommended_movies.forEach((movie) => {
              var li = document.createElement("li");
              li.textContent = movie;
              recommendedList.appendChild(li);
            });
          } else {
            console.error(
              "Invalid response format: Missing or invalid recommended_movies array"
            );
          }
        })
        .catch((error) => {
          console.error("Error fetching recommendation:", error);
        });
      button.click();
    }
  }

  function handleGaze(data) {
    if (!data || !isValidCoordinate(data.x) || !isValidCoordinate(data.y))
      return;

    var x = data.x;
    var y = data.y;
    var currentElement = getElementFromPoint(x, y);

    if (currentElement === previousElement) {
      consecutiveMatches++;
    } else {
      consecutiveMatches = 0;
    }

    if (
      consecutiveMatches === 1 &&
      currentElement &&
      currentElement.tagName === "BUTTON"
    ) {
      simulateButtonClick(currentElement);
      consecutiveMatches = 0;
    }

    previousElement = currentElement;
  }

  startCalibrationButton.addEventListener("click", function () {
    webgazer.setRegression("ridge").setTracker("clmtrackr").begin();

    webgazer
      .showPredictionPoints(true)
      .showFaceOverlay(true)
      .showVideo(true)
      .begin()
      .then(function () {
        console.log("Webgazer is ready");
        webgazer.setGazeListener(handleGaze);
      })
      .catch(function (err) {
        console.error("Webgazer initialization failed:", err);
      });
  });

  window.addEventListener("beforeunload", function () {
    webgazer.end();
  });
});
