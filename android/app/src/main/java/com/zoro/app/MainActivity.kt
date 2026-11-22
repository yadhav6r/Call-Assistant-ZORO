package com.zoro.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import com.zoro.app.ui.ZoroApp
import com.zoro.app.ui.ZoroViewModel

class MainActivity : ComponentActivity() {
    private val viewModel: ZoroViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { ZoroApp(viewModel) }
    }
}
