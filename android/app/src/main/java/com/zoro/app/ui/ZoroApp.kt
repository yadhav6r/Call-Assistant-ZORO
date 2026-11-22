package com.zoro.app.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.zoro.app.data.Contact

private val modes = listOf(
    "available" to "Available",
    "busy" to "Busy",
    "meeting" to "Meeting",
    "sleeping" to "Sleeping",
    "driving" to "Driving",
    "dnd" to "Do not disturb",
    "emergency" to "Emergency",
)

@Composable
fun ZoroApp(viewModel: ZoroViewModel) {
    val state by viewModel.state
    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            if (state.profile == null) {
                SignInScreen(
                    loading = state.loading,
                    error = state.error,
                    onSignIn = viewModel::signIn,
                    onCreateAccount = viewModel::createAccount,
                )
            } else {
                DashboardScreen(
                    state = state,
                    onSelectMode = viewModel::setMode,
                    onRefresh = viewModel::refreshDashboard,
                    onSignOut = viewModel::signOut,
                    onAddContact = viewModel::addContact,
                    onUpdateContact = viewModel::updateContact,
                    onDeleteContact = viewModel::deleteContact,
                    onStartSimulation = viewModel::startSimulation,
                    onSendSimulationTurn = viewModel::sendSimulationTurn,
                    onEndSimulation = viewModel::endSimulation,
                )
            }
        }
    }
}

@Composable
private fun SignInScreen(
    loading: Boolean,
    error: String?,
    onSignIn: (String, String) -> Unit,
    onCreateAccount: (String, String) -> Unit,
) {
    var email by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }
    var creatingAccount by rememberSaveable { mutableStateOf(false) }

    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.Start,
    ) {
        Text("ZORO", style = MaterialTheme.typography.headlineLarge)
        Spacer(Modifier.height(8.dp))
        Text("Your communication assistant", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(28.dp))
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(12.dp))
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(16.dp))
        if (error != null) {
            Text(error, color = MaterialTheme.colorScheme.error)
            Spacer(Modifier.height(8.dp))
        }
        Button(
            onClick = {
                if (creatingAccount) onCreateAccount(email, password) else onSignIn(email, password)
            },
            enabled = !loading && email.isNotBlank() && password.length >= 12,
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (loading) CircularProgressIndicator()
            else Text(if (creatingAccount) "Create account" else "Sign in")
        }
        TextButton(onClick = { creatingAccount = !creatingAccount }, enabled = !loading) {
            Text(if (creatingAccount) "Already have an account? Sign in" else "Create an account")
        }
        Spacer(Modifier.height(12.dp))
        Text(
            "Development sign-in only. Use at least 12 characters for a new password.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun DashboardScreen(
    state: HomeState,
    onSelectMode: (String) -> Unit,
    onRefresh: () -> Unit,
    onSignOut: () -> Unit,
    onAddContact: (String, String) -> Unit,
    onUpdateContact: (Contact, String, String) -> Unit,
    onDeleteContact: (Contact) -> Unit,
    onStartSimulation: (String) -> Unit,
    onSendSimulationTurn: (String) -> Unit,
    onEndSimulation: () -> Unit,
) {
    var selectedTab by rememberSaveable { mutableStateOf(0) }
    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Text("●") },
                    label = { Text("Home") },
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Text("☎") },
                    label = { Text("Contacts") },
                )
                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    icon = { Text("◉") },
                    label = { Text("Simulate") },
                )
            }
        },
    ) { padding ->
        if (selectedTab == 0) {
            HomeScreen(
                state = state,
                onSelectMode = onSelectMode,
                onRefresh = onRefresh,
                onSignOut = onSignOut,
                contentPadding = padding,
            )
        } else if (selectedTab == 1) {
            ContactsScreen(
                state = state,
                onAddContact = onAddContact,
                onUpdateContact = onUpdateContact,
                onDeleteContact = onDeleteContact,
                contentPadding = padding,
            )
        } else {
            SimulationScreen(
                state = state,
                onStart = onStartSimulation,
                onSendTurn = onSendSimulationTurn,
                onEnd = onEndSimulation,
                contentPadding = padding,
            )
        }
    }
}

@Composable
private fun SimulationScreen(
    state: HomeState,
    onStart: (String) -> Unit,
    onSendTurn: (String) -> Unit,
    onEnd: () -> Unit,
    contentPadding: PaddingValues,
) {
    var callerName by rememberSaveable { mutableStateOf("") }
    var message by rememberSaveable { mutableStateOf("") }
    val call = state.simulatedCall
    Column(
        modifier = Modifier.fillMaxSize().padding(contentPadding).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Text simulation", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Development mock only. It does not place calls or use a live AI. Responses follow fixed safety rules.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (call == null) {
            OutlinedTextField(
                value = callerName,
                onValueChange = { callerName = it },
                label = { Text("Caller name (optional)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Button(onClick = { onStart(callerName) }, enabled = !state.loading) {
                Text("Start mock conversation")
            }
        } else {
            Text("Caller: ${call.callerName ?: "Unknown"} · ${call.status}")
            LazyColumn(
                modifier = Modifier.weight(1f).fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(call.events, key = { it.id }) { event ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(12.dp)) {
                            Text(
                                if (event.speaker == "caller") "Caller" else "ZORO · AI",
                                style = MaterialTheme.typography.labelMedium,
                            )
                            Text(event.content)
                            val intent = event.policy["intent"]?.toString()
                            val decision = event.policy["decision"]?.toString()
                            if (intent != null && event.speaker == "assistant") {
                                Text("Policy: $intent · ${decision ?: "recorded"}", style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }
            }
            if (call.status == "active") {
                OutlinedTextField(
                    value = message,
                    onValueChange = { message = it },
                    label = { Text("Type a caller message") },
                    modifier = Modifier.fillMaxWidth(),
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { onSendTurn(message); message = "" },
                        enabled = !state.loading && message.isNotBlank(),
                    ) { Text("Send") }
                    OutlinedButton(onClick = onEnd, enabled = !state.loading) { Text("End") }
                }
            } else {
                OutlinedButton(onClick = { callerName = ""; message = ""; onStart("") }) {
                    Text("Start another simulation")
                }
            }
        }
        if (state.error != null) Text(state.error, color = MaterialTheme.colorScheme.error)
        if (state.loading) CircularProgressIndicator()
    }
}

@Composable
private fun HomeScreen(
    state: HomeState,
    onSelectMode: (String) -> Unit,
    onRefresh: () -> Unit,
    onSignOut: () -> Unit,
    contentPadding: PaddingValues,
) {
    val profile = state.profile ?: return
    val availability = state.availability
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(contentPadding),
        contentPadding = PaddingValues(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column {
                    Text("Good day, ${profile.displayName}", style = MaterialTheme.typography.headlineSmall)
                    Text(profile.email, style = MaterialTheme.typography.bodyMedium)
                }
                TextButton(onClick = onSignOut) { Text("Sign out") }
            }
        }
        item {
            Card(shape = RoundedCornerShape(20.dp), modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(18.dp)) {
                    Text("ZORO service", style = MaterialTheme.typography.titleMedium)
                    Text(if (availability != null) "Connected to your account" else "Loading settings…")
                    if (availability != null) {
                        Spacer(Modifier.height(8.dp))
                        Text("Mode: ${availability.mode.replaceFirstChar { it.uppercase() }}")
                        Text("Settings synced: ${availability.synchronizedAt}", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
        item {
            Text("Availability", style = MaterialTheme.typography.titleLarge)
            Text("Choose how ZORO handles calls routed to it.", style = MaterialTheme.typography.bodyMedium)
        }
        items(modes) { (mode, label) ->
            if (availability?.mode == mode) {
                Button(
                    onClick = { onSelectMode(mode) },
                    enabled = !state.loading,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("$label  ·  Current") }
            } else {
                OutlinedButton(
                    onClick = { onSelectMode(mode) },
                    enabled = !state.loading && availability != null,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text(label) }
            }
        }
        item {
            if (state.error != null) {
                Text(state.error, color = MaterialTheme.colorScheme.error)
                TextButton(onClick = onRefresh) { Text("Refresh from server") }
            }
            if (state.loading) CircularProgressIndicator()
        }
    }
}

@Composable
private fun ContactsScreen(
    state: HomeState,
    onAddContact: (String, String) -> Unit,
    onUpdateContact: (Contact, String, String) -> Unit,
    onDeleteContact: (Contact) -> Unit,
    contentPadding: PaddingValues,
) {
    var showAddDialog by rememberSaveable { mutableStateOf(false) }
    var pendingDeleteId by rememberSaveable { mutableStateOf<String?>(null) }
    var editingContactId by rememberSaveable { mutableStateOf<String?>(null) }
    val pendingDelete = state.contacts.firstOrNull { it.id == pendingDeleteId }
    val editingContact = state.contacts.firstOrNull { it.id == editingContactId }

    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(contentPadding),
        contentPadding = PaddingValues(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column {
                    Text("Contacts", style = MaterialTheme.typography.headlineSmall)
                    Text("Manage the people ZORO can recognize.")
                }
                Button(onClick = { showAddDialog = true }) { Text("Add") }
            }
            if (state.error != null) Text(state.error, color = MaterialTheme.colorScheme.error)
            if (state.loading) CircularProgressIndicator()
        }
        if (state.contacts.isEmpty()) {
            item { Text("No contacts yet. Add someone you want ZORO to recognize.") }
        } else {
            items(state.contacts, key = { it.id }) { contact ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(contact.displayName, style = MaterialTheme.typography.titleMedium)
                            Text(contact.phoneE164, style = MaterialTheme.typography.bodyMedium)
                            Text(
                                "${contact.category} · ${contact.trustLevel}",
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                        TextButton(onClick = { editingContactId = contact.id }) { Text("Edit") }
                        TextButton(onClick = { pendingDeleteId = contact.id }) { Text("Delete") }
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        AddContactDialog(
            contact = null,
            onDismiss = { showAddDialog = false },
            onSave = { name, phone ->
                onAddContact(name, phone)
                showAddDialog = false
            },
        )
    }
    editingContact?.let { contact ->
        AddContactDialog(
            contact = contact,
            onDismiss = { editingContactId = null },
            onSave = { name, phone ->
                onUpdateContact(contact, name, phone)
                editingContactId = null
            },
        )
    }
    pendingDelete?.let { contact ->
        AlertDialog(
            onDismissRequest = { pendingDeleteId = null },
            title = { Text("Delete ${contact.displayName}?") },
            text = { Text("This removes the contact from your ZORO directory.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        onDeleteContact(contact)
                        pendingDeleteId = null
                    },
                ) { Text("Delete") }
            },
            dismissButton = {
                TextButton(onClick = { pendingDeleteId = null }) { Text("Cancel") }
            },
        )
    }
}

@Composable
private fun AddContactDialog(
    contact: Contact?,
    onDismiss: () -> Unit,
    onSave: (String, String) -> Unit,
) {
    var name by rememberSaveable(contact?.id) { mutableStateOf(contact?.displayName.orEmpty()) }
    var phone by rememberSaveable(contact?.id) { mutableStateOf(contact?.phoneE164.orEmpty()) }
    val validPhone = phone.startsWith("+") && phone.drop(1).all { it.isDigit() } && phone.length in 8..16

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(if (contact == null) "Add contact" else "Edit contact") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Name") },
                    singleLine = true,
                )
                OutlinedTextField(
                    value = phone,
                    onValueChange = { phone = it },
                    label = { Text("Phone in international format") },
                    placeholder = { Text("+14155552671") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                    singleLine = true,
                )
                Text(
                    "Use + and country code, for example +14155552671.",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onSave(name, phone) },
                enabled = name.isNotBlank() && validPhone,
            ) { Text(if (contact == null) "Add" else "Save") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } },
    )
}




