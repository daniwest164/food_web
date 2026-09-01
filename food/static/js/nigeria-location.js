/* =============================================
   NIGERIA LOCATION PICKER - State/LGA cascading
   Uses: https://raw.githubusercontent.com/Vickylove5223/Nigeria-Dataset/main/data/nigeria-data.json
   ============================================= */

var NigeriaLocation = (function () {
  var API_URL = 'https://raw.githubusercontent.com/Vickylove5223/Nigeria-Dataset/main/data/nigeria-data.json';
  var _cache = null;

  function fetchStates() {
    if (_cache) return Promise.resolve(_cache);
    return fetch(API_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        _cache = data.states.map(function (s) {
          return { name: s.name, lgas: s.lgas.map(function (l) { return l.name; }) };
        });
        return _cache;
      });
  }

  function populateStateDropdown(selectEl, placeholder) {
    selectEl.innerHTML = '<option value="">' + (placeholder || '-- Select State --') + '</option>';
    selectEl.disabled = true;
    return fetchStates().then(function (states) {
      states.forEach(function (s) {
        var opt = document.createElement('option');
        opt.value = s.name;
        opt.textContent = s.name;
        selectEl.appendChild(opt);
      });
      selectEl.disabled = false;
    });
  }

  function populateLGADropdown(stateName, lgaSelectEl, placeholder) {
    lgaSelectEl.innerHTML = '<option value="">' + (placeholder || '-- Select LGA --') + '</option>';
    lgaSelectEl.disabled = true;
    if (!stateName) return Promise.resolve();
    return fetchStates().then(function (states) {
      var state = states.find(function (s) { return s.name === stateName; });
      if (!state) return;
      state.lgas.forEach(function (lga) {
        var opt = document.createElement('option');
        opt.value = lga;
        opt.textContent = lga;
        lgaSelectEl.appendChild(opt);
      });
      lgaSelectEl.disabled = false;
    });
  }

  function bindStateLGA(stateSelectId, lgaSelectId, initialState, initialLga) {
    var stateEl = document.getElementById(stateSelectId);
    var lgaEl = document.getElementById(lgaSelectId);
    if (!stateEl || !lgaEl) return;

    var _initialState = initialState || '';
    var _initialLga = initialLga || '';

    populateStateDropdown(stateEl).then(function () {
      if (_initialState) {
        stateEl.value = _initialState;
        return populateLGADropdown(_initialState, lgaEl).then(function () {
          if (_initialLga) lgaEl.value = _initialLga;
        });
      }
    });

    stateEl.addEventListener('change', function () {
      lgaEl.innerHTML = '<option value="">-- Select LGA --</option>';
      lgaEl.disabled = true;
      if (this.value) {
        populateLGADropdown(this.value, lgaEl);
      }
    });
  }

  return {
    fetchStates: fetchStates,
    populateStateDropdown: populateStateDropdown,
    populateLGADropdown: populateLGADropdown,
    bindStateLGA: bindStateLGA
  };
})();
