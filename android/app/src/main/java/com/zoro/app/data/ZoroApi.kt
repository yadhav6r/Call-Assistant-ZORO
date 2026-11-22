package com.zoro.app.data

import com.google.gson.annotations.SerializedName
import retrofit2.Call
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query


data class Credentials(val email: String, val password: String)
data class RefreshRequest(@SerializedName("refresh_token") val refreshToken: String)
data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("token_type") val tokenType: String,
    @SerializedName("expires_in") val expiresIn: Int,
)
data class Profile(
    val id: String,
    val email: String,
    @SerializedName("display_name") val displayName: String,
    val timezone: String,
    @SerializedName("preferred_language") val preferredLanguage: String,
)
data class Availability(
    val mode: String,
    val version: Int,
    @SerializedName("synchronized_at") val synchronizedAt: String,
)
data class AvailabilityUpdate(
    val mode: String,
    @SerializedName("expected_version") val expectedVersion: Int,
)
data class Contact(
    val id: String,
    @SerializedName("display_name") val displayName: String,
    @SerializedName("phone_e164") val phoneE164: String,
    val category: String,
    @SerializedName("trust_level") val trustLevel: String,
)
data class ContactCreate(
    @SerializedName("display_name") val displayName: String,
    @SerializedName("phone_e164") val phoneE164: String,
)
data class ContactUpdate(
    @SerializedName("display_name") val displayName: String,
    @SerializedName("phone_e164") val phoneE164: String,
)
data class SimulatedCallCreate(
    @SerializedName("caller_name") val callerName: String? = null,
)
data class SimulatedTurnCreate(val text: String)
data class ConversationEvent(
    val id: String,
    val sequence: Int,
    val speaker: String,
    val content: String,
    val policy: Map<String, Any> = emptyMap(),
    @SerializedName("created_at") val createdAt: String,
)
data class SimulatedCall(
    val id: String,
    val channel: String,
    val status: String,
    @SerializedName("caller_name") val callerName: String?,
    @SerializedName("caller_phone_e164") val callerPhoneE164: String?,
    @SerializedName("contact_name") val contactName: String?,
    @SerializedName("availability_mode") val availabilityMode: String,
    @SerializedName("started_at") val startedAt: String,
    @SerializedName("ended_at") val endedAt: String?,
    val events: List<ConversationEvent>,
)

interface ZoroApi {
    @POST("api/v1/auth/register")
    suspend fun register(@Body credentials: Credentials): TokenResponse

    @POST("api/v1/auth/login")
    suspend fun login(@Body credentials: Credentials): TokenResponse

    @POST("api/v1/auth/refresh")
    fun refresh(@Body request: RefreshRequest): Call<TokenResponse>

    @POST("api/v1/auth/logout")
    suspend fun logout(@Header("Authorization") authorization: String): Response<Unit>

    @GET("api/v1/profile")
    suspend fun profile(): Profile

    @GET("api/v1/availability")
    suspend fun availability(): Availability

    @PUT("api/v1/availability")
    suspend fun setAvailability(@Body update: AvailabilityUpdate): Availability

    @GET("api/v1/contacts")
    suspend fun contacts(
        @Query("limit") limit: Int = 100,
        @Query("offset") offset: Int = 0,
    ): List<Contact>

    @POST("api/v1/contacts")
    suspend fun createContact(@Body contact: ContactCreate): Contact

    @PATCH("api/v1/contacts/{contactId}")
    suspend fun updateContact(
        @Path("contactId") contactId: String,
        @Body contact: ContactUpdate,
    ): Contact

    @DELETE("api/v1/contacts/{contactId}")
    suspend fun deleteContact(@Path("contactId") contactId: String): Response<Unit>

    @POST("api/v1/simulated-calls")
    suspend fun startSimulation(@Body request: SimulatedCallCreate): SimulatedCall

    @POST("api/v1/simulated-calls/{callId}/turns")
    suspend fun sendSimulationTurn(
        @Path("callId") callId: String,
        @Body request: SimulatedTurnCreate,
    ): SimulatedCall

    @POST("api/v1/simulated-calls/{callId}/end")
    suspend fun endSimulation(@Path("callId") callId: String): SimulatedCall
}
