/* =============================================
   NIGERIA LOCATION PICKER - State/LGA cascading
   Uses: https://raw.githubusercontent.com/Vickylove5223/Nigeria-Dataset/main/data/nigeria-data.json
   ============================================= */

var NigeriaLocation = (function () {
  var API_URL = 'https://raw.githubusercontent.com/Vickylove5223/Nigeria-Dataset/main/data/nigeria-data.json';
  var _cache = null;

  function requestDataset(attempt) {
    return fetch(API_URL, { headers: { 'Accept': 'application/json' } })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .catch(function (err) {
        // One automatic retry: raw.githubusercontent is occasionally flaky
        // and a dropped request used to leave the dropdown stuck disabled.
        if (attempt < 2) return requestDataset(attempt + 1);
        throw err;
      });
  }

  function fetchStates() {
    if (_cache) return Promise.resolve(_cache);
    return requestDataset(1).then(function (data) {
      if (!data || !Array.isArray(data.states)) throw new Error('Unexpected dataset shape');
      _cache = data.states.map(function (s) {
        var lgas = Array.isArray(s.lgas) ? s.lgas : [];
        return {
          name: s.name,
          lgas: lgas.map(function (l) { return typeof l === 'string' ? l : l.name; })
                  .filter(Boolean)
        };
      });
      return _cache;
    });
  }

  function setFailure(selectEl, message) {
    selectEl.innerHTML = '<option value="">' + message + '</option>';
    selectEl.disabled = true;
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
    }).catch(function (err) {
      // Never leave the dropdown silently disabled — say what went wrong.
      if (window.console) console.error('NigeriaLocation: state list failed —', err);
      setFailure(selectEl, 'Could not load states. Check your connection.');
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
    }).catch(function (err) {
      if (window.console) console.error('NigeriaLocation: LGA list failed —', err);
      setFailure(lgaSelectEl, 'Could not load LGAs. Check your connection.');
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
