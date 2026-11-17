import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import hudson.security.ACL
import hudson.util.Secret
import jenkins.model.Jenkins
import org.jenkinsci.plugins.github.GitHubPlugin
import org.jenkinsci.plugins.github.config.HookSecretConfig
import org.jenkinsci.plugins.plaincredentials.StringCredentials
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl

import java.security.SecureRandom
import java.util.Base64

def jenkins = Jenkins.get()
def credentialId = 'kerjayuk-github-webhook-secret'
def credential = CredentialsProvider.lookupCredentials(
    StringCredentials.class,
    jenkins,
    ACL.SYSTEM
).find { it.id == credentialId }

String webhookSecret
if (credential == null) {
    byte[] bytes = new byte[32]
    new SecureRandom().nextBytes(bytes)
    webhookSecret = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes)
    credential = new StringCredentialsImpl(
        CredentialsScope.GLOBAL,
        credentialId,
        'GitHub webhook signature secret for KerjaYuk',
        Secret.fromString(webhookSecret)
    )
    SystemCredentialsProvider.getInstance().getStore().addCredentials(Domain.global(), credential)
    println("Created Jenkins credential ${credentialId}.")
} else {
    webhookSecret = credential.getSecret().getPlainText()
    println("Using existing Jenkins credential ${credentialId}.")
}

def githubConfig = GitHubPlugin.configuration()
githubConfig.setHookSecretConfigs([new HookSecretConfig(credentialId, 'SHA256')])
githubConfig.save()

def secretFile = new File(jenkins.getRootDir(), 'secrets/kerjayuk-github-webhook-secret.txt')
secretFile.parentFile.mkdirs()
secretFile.setText(webhookSecret + System.lineSeparator(), 'UTF-8')
secretFile.setReadable(false, false)
secretFile.setWritable(false, false)
secretFile.setReadable(true, true)
secretFile.setWritable(true, true)
println('Configured GitHub webhook signature validation with SHA-256.')
