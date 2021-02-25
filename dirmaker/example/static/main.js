function filterList(sel, itemSelector) {
	// Hide all items.
	document.querySelectorAll(itemSelector).forEach(e => {
		e.style.display = "none";
	});

	if (sel.length === 0) {
		return;
	}

	// List of attribute selector queries for each value. eg:
	// #items li[data-language*=malayalam|], #items li[data-language*=kannada|] ...
	const q = sel.map(v => `${itemSelector}[data-${v.taxonomy}*='${v.value}|']`);

	// Show the matched items.
	document.querySelectorAll(q.join(", ")).forEach(e => {
		e.style.display = "block";
	});
}

function onFilter() {
	// Get the value of all checked items for all the taxonomy groups.
	const taxItems = Array.from(document.querySelectorAll(`#filters input[type=checkbox]:checked`));
	const sel = taxItems.map((e) => {
		return { taxonomy: e.dataset.taxonomy, value: e.value }
	});

	filterList(sel, "#items .item");
}

const reClean = new RegExp(/[^a-z0-9\s]+/g);
const reSpaces = new RegExp(/\s+/g);
function tokenize(str) {
	return str.toLowerCase().replace(reClean, "").replace(reSpaces, " ").split(" ").filter((c) => c !== "");
}

// UI hooks.
(function() {
	// Mobile burger menu.
	document.querySelector("#burger").onclick = (e) => {
		e.preventDefault();
		const f = document.querySelector("#sidebar");
		f.style.display = f.style.display === "block" ? "none" : "block";
	};


	// Text search.
	let isSearching = false;
	document.querySelector("#search").oninput = function(e) {
		if (isSearching) {
			return true;
		}

		isSearching = true;
		window.setTimeout(() => {
			isSearching = false;
		}, 100);

		if (e.target.value.length < 3) {
			document.querySelectorAll("#items .item").forEach(e => e.style.display = 'block')
			return;
		}
		const search = tokenize(e.target.value);

		document.querySelectorAll("#items .item").forEach(e => {
			// Tokenize the text title and description of all the items.
			let txt = tokenize(e.querySelector(".title").innerText + " " + e.querySelector(".description").innerText);

			// Search input against the item tokens. Every token in the search input should match.
			let has = 0;
			for (let i = 0; i < search.length; i++) {
				for (let j = 0; j < txt.length; j++) {
					if (txt[j].indexOf(search[i]) > -1) {
						has++;
						break;
					}
				}
			}

			e.style.display = has === search.length ? "block" : "none";
		});
	};


	// Filter display toggle.
	document.querySelector("#toggle-filters").onclick = (e) => {
		e.preventDefault();

		const f = document.querySelector("#filters");
		f.style.display = f.style.display === "block" ? "none" : "block";
	};

	// Toggle filter checkbox selections.
	document.querySelectorAll(".toggle-filters").forEach(el => {
		el.onclick = (e) => {
			e.preventDefault();

			// Check or uncheck all filter checkboxes with the toggle item's dataset.taxonomy.
			const tax = e.target.dataset.taxonomy;
			document.querySelectorAll(`#filters input[data-taxonomy=${tax}]`).forEach(el => {
				el.checked = e.target.dataset.state === "on" ? false : true;
			});

			e.target.dataset.state = e.target.dataset.state === "on" ? "off" : "on";

			// Trigger the filter.
			onFilter();
		};
	});

	// Taxonomies filters.
	document.querySelectorAll("#filters input[type=checkbox]").forEach(el => {
		el.onchange = () => {
			onFilter();
		};
	});

	// 'View all' link on taxonomies.
	document.querySelectorAll(".reveal").forEach(el => {
		el.onclick = (e) => {
			e.preventDefault();

			const cls = e.target.parentNode.classList;
			if (cls.contains("visible")) {
				console.log("yes", cls.contains("visible"));
				cls.remove("visible");
			} else {
				cls.add("visible");
				console.log("no", cls.contains("visible"));
			}
		};
	});

})();
