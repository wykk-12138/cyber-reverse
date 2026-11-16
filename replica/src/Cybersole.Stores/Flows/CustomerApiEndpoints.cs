namespace Cybersole.Stores.Flows;

/// <summary>
/// The account-management API the image exposes at <c>/customer/v1/</c>, recovered in R902.
///
/// <para>
/// <b>What is observed.</b> Ten path literals exist in the image. They cover address create, delete, list and update;
/// reading the current customer, checking whether one exists, guest registration, ordinary registration and login;
/// and sending a verification code. Every one is listed verbatim below.
/// </para>
///
/// <para>
/// <b>What is inference, and it is a larger gap than usual.</b> None of these ten carries a host in its own literal.
/// R901's canonical measurement puts them in the hostless bucket, which means the image does not say which store's
/// account API this is. The family name is generic enough that several stores could use the same paths, and the
/// replica has no <c>/customer/v1/</c> literal anywhere, so there is nothing on the other side to compare against
/// either. Treat these as endpoints that exist in the image and whose owner is unknown.
/// </para>
///
/// <para>
/// <b>What is absent.</b> Request bodies, response shapes, authentication scheme and which flow calls them. No step
/// uses these constants for that reason; a step would have to invent all four.
/// </para>
///
/// <para>
/// Reproof: <c>python tools\endpoint_coverage.py -v</c> lists these ten under <c>hostless</c>, and
/// <c>analysis/coverage_extract.py</c> is what produced the path set it reads.
/// </para>
/// </summary>
public static class CustomerApiEndpoints
{
    /// <summary>Create an address on the account.</summary>
    public const string AddressAdd = "/customer/v1/address/add";

    /// <summary>Delete an address.</summary>
    public const string AddressDelete = "/customer/v1/address/del";

    /// <summary>List the account's addresses.</summary>
    public const string AddressList = "/customer/v1/address/list";

    /// <summary>Update an address.</summary>
    public const string AddressUpdate = "/customer/v1/address/update";

    /// <summary>Read the signed-in customer.</summary>
    public const string CustomerApp = "/customer/v1/customer/app";

    /// <summary>Whether an account exists for a given identity — the check a signup flow makes first.</summary>
    public const string CustomerExist = "/customer/v1/customer/exist";

    /// <summary>Register as a guest, without creating an account.</summary>
    public const string GuestRegister = "/customer/v1/customer/guest/register";

    /// <summary>Sign in.</summary>
    public const string Login = "/customer/v1/customer/login";

    /// <summary>Create an account.</summary>
    public const string Register = "/customer/v1/customer/register";

    /// <summary>Send a verification code — email or SMS, and which is not recorded in the path.</summary>
    public const string VerificationSend = "/customer/v1/verification/send";

    /// <summary>Every path above, in the order the operations would be used during a signup.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CustomerExist, Register, GuestRegister, Login, VerificationSend,
        AddressAdd, AddressList, AddressUpdate, AddressDelete, CustomerApp,
    };

    /// <summary>
    /// True: no literal holding any of these paths also holds a host, so the owning store is unknown rather than
    /// merely unconfirmed. Contrast <see cref="VansEndpoints.OwnershipIsInference"/>, which is false because that
    /// family's paths do share literals with their host.
    /// </summary>
    public const bool OwnerIsUnknown = true;

    /// <summary>Ten, which is what the image holds. Named so a partial copy is visible as partial.</summary>
    public const int RecoveredPathCount = 10;
}
