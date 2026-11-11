package com.chitra.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { ChitraApp() }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChitraApp() {
    var tab by remember { mutableStateOf("Home") }
    val tabs = listOf("Home", "Shorts", "Upload", "Subscriptions", "You")
    MaterialTheme {
        Scaffold(
            topBar = { TopAppBar(title = { Text("Chitra") }) },
            bottomBar = { NavigationBar {
                tabs.forEach { item ->
                    NavigationBarItem(selected = tab == item, onClick = { tab = item },
                        icon = { Text(item.take(1)) }, label = { Text(item) })
                }
            } }
        ) { padding ->
            LazyColumn(Modifier.fillMaxSize().padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                item { Text(when(tab) {
                    "Home" -> "Recommended videos"
                    "Shorts" -> "Chitra Shorts"
                    "Upload" -> "Upload a video"
                    "Subscriptions" -> "Your subscriptions"
                    else -> "Creator Studio"
                }, style = MaterialTheme.typography.headlineSmall) }
                item { Text(when(tab) {
                    "Upload" -> "Upload UI is ready for API integration. Shorts limit: 120 seconds."
                    "You" -> "Creator monetization is eligibility-based and requires review."
                    else -> "Connect the Chitra API to load live content."
                }) }
                items(6) { index ->
                    Card(Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(16.dp)) {
                            Text("${tab} item ${index + 1}", style = MaterialTheme.typography.titleMedium)
                            Spacer(Modifier.height(6.dp))
                            Text("Video card placeholder — API and HLS player integration pending.")
                        }
                    }
                }
            }
        }
    }
}
