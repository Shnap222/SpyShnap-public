
    function closeSearch() {
        let search = document.getElementById("search");
        let searchInput = document.getElementById("searchInput")
        let button = document.getElementById("searchButton")

        if (searchInput.value.length === 0) {
            button.onclick = function () {
                openSearch()
            }
            searchInput.classList.remove("inputOpened")
            searchInput.classList.add("inputClosed")
            search.classList.remove("formOpened")
        }
        else
        {
            search.submit();
        }



    }

    function openSearch() {
        let search = document.getElementById("search");
        let button = document.getElementById("searchButton")
        let searchInput = document.getElementById("searchInput")


        search.classList.add("formOpened")
        searchInput.classList.remove("inputClosed")
        searchInput.classList.add("inputOpened")
        button.onclick = function () {
            closeSearch()
        }

    }


    function redirectPage(ip,id) {
        window.location.replace("clients/" + ip+","+id);


    }


