package com.zoro.app.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.zoro.app.data.ApiClient
import com.zoro.app.data.Availability
import com.zoro.app.data.AvailabilityUpdate
import com.zoro.app.data.Contact
import com.zoro.app.data.ContactCreate
import com.zoro.app.data.ContactUpdate
import com.zoro.app.data.SimulatedCall
import com.zoro.app.data.SimulatedCallCreate
import com.zoro.app.data.SimulatedTurnCreate
import com.zoro.app.data.Credentials
import com.zoro.app.data.Profile
import kotlinx.coroutines.launch
import retrofit2.HttpException


data class HomeState(
    val loading: Boolean = false,
    val profile: Profile? = null,
    val availability: Availability? = null,
    val contacts: List<Contact> = emptyList(),
    val simulatedCall: SimulatedCall? = null,
    val error: String? = null,
)

class ZoroViewModel(application: Application) : AndroidViewModel(application) {
    private val client = ApiClient.create(application)
    private val api = client.first
    private val tokenStore = client.second
    val state = androidx.compose.runtime.mutableStateOf(HomeState())

    init {
        if (tokenStore.accessToken() != null) refreshDashboard()
    }

    fun signIn(email: String, password: String) = authenticate(email, password, createAccount = false)

    fun createAccount(email: String, password: String) = authenticate(email, password, createAccount = true)

    private fun authenticate(email: String, password: String, createAccount: Boolean) {
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val credentials = Credentials(email.trim(), password)
                val tokens = if (createAccount) api.register(credentials) else api.login(credentials)
                tokenStore.save(tokens.accessToken, tokens.refreshToken)
                loadDashboard()
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }

    fun refreshDashboard() {
        viewModelScope.launch { loadDashboard() }
    }

    fun setMode(mode: String) {
        val version = state.value.availability?.version ?: return
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val updated = api.setAvailability(AvailabilityUpdate(mode, version))
                state.value = state.value.copy(loading = false, availability = updated)
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
                if (error is HttpException && error.code() == 409) loadDashboard()
            }
        }
    }

    fun addContact(displayName: String, phoneE164: String) {
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val created = api.createContact(ContactCreate(displayName.trim(), phoneE164.trim()))
                state.value = state.value.copy(
                    loading = false,
                    contacts = (state.value.contacts + created).sortedBy { it.displayName.lowercase() },
                )
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }

    fun updateContact(contact: Contact, displayName: String, phoneE164: String) {
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val updated = api.updateContact(
                    contact.id,
                    ContactUpdate(displayName.trim(), phoneE164.trim()),
                )
                state.value = state.value.copy(
                    loading = false,
                    contacts = state.value.contacts.map { if (it.id == updated.id) updated else it }
                        .sortedBy { it.displayName.lowercase() },
                )
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }
    fun deleteContact(contact: Contact) {
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                api.deleteContact(contact.id)
                state.value = state.value.copy(
                    loading = false,
                    contacts = state.value.contacts.filterNot { it.id == contact.id },
                )
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }

    fun startSimulation(callerName: String) {
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val name = callerName.trim().ifBlank { null }
                val call = api.startSimulation(SimulatedCallCreate(callerName = name))
                state.value = state.value.copy(loading = false, simulatedCall = call)
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }

    fun sendSimulationTurn(text: String) {
        val call = state.value.simulatedCall?.takeIf { it.status == "active" } ?: return
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val updated = api.sendSimulationTurn(call.id, SimulatedTurnCreate(text.trim()))
                state.value = state.value.copy(loading = false, simulatedCall = updated)
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }

    fun endSimulation() {
        val call = state.value.simulatedCall?.takeIf { it.status == "active" } ?: return
        state.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val updated = api.endSimulation(call.id)
                state.value = state.value.copy(loading = false, simulatedCall = updated)
            } catch (error: Exception) {
                state.value = state.value.copy(loading = false, error = readableError(error))
            }
        }
    }

    fun signOut() {
        viewModelScope.launch {
            try {
                tokenStore.accessToken()?.let { api.logout("Bearer $it") }
            } catch (_: Exception) {
                // Clear local credentials even when the server cannot be reached.
            } finally {
                tokenStore.clear()
                state.value = HomeState()
            }
        }
    }

    private suspend fun loadDashboard() {
        state.value = state.value.copy(loading = true, error = null)
        try {
            val profile = api.profile()
            val availability = api.availability()
            val contacts = api.contacts()
            state.value = HomeState(profile = profile, availability = availability, contacts = contacts)
        } catch (error: Exception) {
            state.value = state.value.copy(loading = false, error = readableError(error))
        }
    }

    private fun readableError(error: Exception): String = when (error) {
        is HttpException -> when (error.code()) {
            401 -> "Session expired. Please sign in again."
            404 -> "That record could not be found."
            409 -> "That change conflicts with current data. Refresh and try again."
            else -> "The server could not complete that request (${error.code()})."
        }
        else -> "Could not reach ZORO. Check the API address and connection."
    }
}



