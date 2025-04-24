document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("searchInput")
  const tableBody = document.querySelector("#usersTable tbody")
  let allUsers = []

  async function loadUsers() {
    const res = await fetch("/api/users")
    allUsers = await res.json()
    renderTable(allUsers)
    searchInput.addEventListener("input", () => {
      const filtered = allUsers.filter(u => u.nombre_completo.toLowerCase().includes(searchInput.value.toLowerCase()) || u.id.toString().includes(searchInput.value))
      renderTable(filtered)
    })
  }

  function renderTable(data) {
    tableBody.innerHTML = ""
    data.forEach(u => {
      const tr = document.createElement("tr")
      tr.innerHTML = `
        <td>${u.id}</td>
        <td>${u.nombre_completo}</td>
        <td>${u.curp || "No ingresada"}</td>
        <td>${u.rfc || "No ingresada"}</td>
        <td><button class="btn btn-outline-primary btn-sm" onclick="showUserDetails(${u.id})"><i class="fa-solid fa-plus"></i></button></td>
        <td><button class="btn btn-outline-secondary btn-sm" onclick="openUploadForm(${u.id}, '${u.nombre_completo}')"><i class="fa-solid fa-upload"></i></button></td>
      `
      tableBody.appendChild(tr)
    })
  }

  window.showUserDetails = async function(id) {
    const res = await fetch(`/api/users/${id}`)
    const data = await res.json()
    document.getElementById("modalUserId").textContent = data.id
    document.getElementById("modalUserName").textContent = data.nombre_completo
    const fields = document.querySelectorAll("#modalUserFields li span")
    fields[0].textContent = data.curp || "No ingresada"
    fields[1].textContent = data.rfc || "No ingresada"
    fields[2].textContent = data.imss || "No ingresada"
    fields[3].textContent = data.fiscal || "No ingresada"
    fields[4].textContent = data.cursos || "No ingresada"
    fields[5].textContent = data.cedulas || "No ingresada"
    new bootstrap.Modal(document.getElementById('userDetailsModal')).show()
  }

  window.openUploadForm = function(id, name) {
    document.getElementById("uploadUserId").value = id
    document.getElementById("uploadUserName").textContent = name
    new bootstrap.Modal(document.getElementById('uploadModal')).show()
  }

  const uploadForm = document.getElementById("uploadForm")
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault()
      const formData = new FormData(uploadForm)
      const res = await fetch("/upload/document", {
        method: "POST",
        body: formData
      })
      const result = await res.json()
      alert("Resultado: " + JSON.stringify(result))
      bootstrap.Modal.getInstance(document.getElementById("uploadModal")).hide()
      await loadUsers()
    })
  }

  loadUsers()
})
