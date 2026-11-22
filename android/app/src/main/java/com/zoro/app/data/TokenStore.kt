package com.zoro.app.data

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/** Encrypts session tokens with an Android Keystore AES-GCM key. */
class TokenStore(context: Context) {
    private val preferences = context.getSharedPreferences("zoro_session", Context.MODE_PRIVATE)

    @Synchronized
    fun save(accessToken: String, refreshToken: String) {
        preferences.edit()
            .putString(ACCESS_KEY, encrypt(accessToken))
            .putString(REFRESH_KEY, encrypt(refreshToken))
            .apply()
    }

    @Synchronized
    fun accessToken(): String? = preferences.getString(ACCESS_KEY, null)?.let(::decrypt)

    @Synchronized
    fun refreshToken(): String? = preferences.getString(REFRESH_KEY, null)?.let(::decrypt)

    @Synchronized
    fun clear() {
        preferences.edit().clear().apply()
    }

    private fun encrypt(value: String): String {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey())
        val encrypted = cipher.iv + cipher.doFinal(value.toByteArray(Charsets.UTF_8))
        return Base64.encodeToString(encrypted, Base64.NO_WRAP)
    }

    private fun decrypt(value: String): String {
        val decoded = Base64.decode(value, Base64.NO_WRAP)
        val iv = decoded.copyOfRange(0, GCM_IV_BYTES)
        val ciphertext = decoded.copyOfRange(GCM_IV_BYTES, decoded.size)
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, secretKey(), GCMParameterSpec(GCM_TAG_BITS, iv))
        return cipher.doFinal(ciphertext).toString(Charsets.UTF_8)
    }

    private fun secretKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        (keyStore.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
        generator.init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build(),
        )
        return generator.generateKey()
    }

    private companion object {
        const val ACCESS_KEY = "access"
        const val REFRESH_KEY = "refresh"
        const val KEY_ALIAS = "zoro.session.tokens"
        const val ANDROID_KEYSTORE = "AndroidKeyStore"
        const val TRANSFORMATION = "AES/GCM/NoPadding"
        const val GCM_IV_BYTES = 12
        const val GCM_TAG_BITS = 128
    }
}
