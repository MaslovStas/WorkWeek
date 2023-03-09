"use strict";

document.addEventListener("DOMContentLoaded", () => {
	const form = document.querySelector("#form");
	const nameInput = form.name;
	const phoneInput = form.phone;

	for (let input of [nameInput, phoneInput]) {
		for (let event of ["input", "focus"]) {
			input.addEventListener(event, () =>
				inputValidate(input) ? inputSubmit(input) : inputFailed(input)
			);
		}
	}

	function inputValidate(input) {
		if (input.name == "phone") {
			return input.value.length == 18;
		}
		return input.value.length != 0;
	}

	function inputCheck(input) {
		inputValidate(input) ? inputSubmit(input) : inputFailed(input);
	}

	function inputSubmit(input) {
		input.previousElementSibling.className = "bi bi-check2 text-success";
	}

	function inputFailed(input) {
		input.previousElementSibling.className = "bi bi-x-lg text-danger";
	}
});
