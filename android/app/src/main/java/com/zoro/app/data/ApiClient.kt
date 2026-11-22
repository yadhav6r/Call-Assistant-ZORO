package com.zoro.app.data

import android.content.Context
import com.zoro.app.BuildConfig
import okhttp3.Authenticator
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    fun create(context: Context): Pair<ZoroApi, TokenStore> {
        val tokenStore = TokenStore(context.applicationContext)
        val unauthenticatedApi = retrofit(OkHttpClient()).create(ZoroApi::class.java)
        val authenticatedClient = OkHttpClient.Builder()
            .addInterceptor(BearerTokenInterceptor(tokenStore))
            .authenticator(RefreshAuthenticator(tokenStore, unauthenticatedApi))
            .build()
        return retrofit(authenticatedClient).create(ZoroApi::class.java) to tokenStore
    }

    private fun retrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .client(client)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}

private class BearerTokenInterceptor(private val tokenStore: TokenStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val path = request.url.encodedPath
        if (path.endsWith("/auth/login") || path.endsWith("/auth/register") || path.endsWith("/auth/refresh")) {
            return chain.proceed(request)
        }
        val token = tokenStore.accessToken() ?: return chain.proceed(request)
        return chain.proceed(
            request.newBuilder().header("Authorization", "Bearer $token").build(),
        )
    }
}

private class RefreshAuthenticator(
    private val tokenStore: TokenStore,
    private val refreshApi: ZoroApi,
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (responseCount(response) > 1) return null
        val failedToken = response.request.header("Authorization")?.removePrefix("Bearer ")
            ?: return null

        synchronized(tokenStore) {
            val currentAccessToken = tokenStore.accessToken() ?: return null
            if (currentAccessToken != failedToken) {
                return response.request.newBuilder()
                    .header("Authorization", "Bearer $currentAccessToken")
                    .build()
            }
            val refreshToken = tokenStore.refreshToken() ?: return null
            val result = try {
                refreshApi.refresh(RefreshRequest(refreshToken)).execute()
            } catch (_: Exception) {
                return null
            }
            if (result.code() == 401) {
                tokenStore.clear()
                return null
            }
            val tokens = result.body()?.takeIf { result.isSuccessful } ?: return null
            tokenStore.save(tokens.accessToken, tokens.refreshToken)
            return response.request.newBuilder()
                .header("Authorization", "Bearer ${tokens.accessToken}")
                .build()
        }
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        return count
    }
}
