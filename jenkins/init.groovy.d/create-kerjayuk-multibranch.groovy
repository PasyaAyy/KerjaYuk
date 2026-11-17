import java.util.EnumSet

import org.jenkinsci.plugins.github_branch_source.ApiRateLimitChecker
import org.jenkinsci.plugins.github_branch_source.GitHubConfiguration
import jenkins.branch.BranchSource
import jenkins.model.Jenkins
import jenkins.scm.api.mixin.ChangeRequestCheckoutStrategy
import org.jenkinsci.plugins.github_branch_source.BranchDiscoveryTrait
import org.jenkinsci.plugins.github_branch_source.GitHubSCMSource
import org.jenkinsci.plugins.github_branch_source.OriginPullRequestDiscoveryTrait
import org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject

def jenkins = Jenkins.get()

def githubConfiguration = GitHubConfiguration.get()
if (githubConfiguration.getApiRateLimitChecker() != ApiRateLimitChecker.ThrottleOnOver) {
    githubConfiguration.setApiRateLimitChecker(ApiRateLimitChecker.ThrottleOnOver)
    println('Configured GitHub API throttling to wait only near the rate limit.')
}

def projectName = 'KerjaYuk'
def project = jenkins.getItem(projectName)
def createdProject = project == null

if (project == null) {
    project = jenkins.createProject(WorkflowMultiBranchProject.class, projectName)
    def source = new GitHubSCMSource('PasyaAyy', 'KerjaYuk', null, false)
    source.getTraits().add(new BranchDiscoveryTrait(BranchDiscoveryTrait.ALL_BRANCHES))
    source.getTraits().add(new OriginPullRequestDiscoveryTrait(
        EnumSet.of(ChangeRequestCheckoutStrategy.MERGE)
    ))

    project.getSourcesList().add(new BranchSource(source))
    project.setDescription('KerjaYuk Multibranch Pipeline: branches and pull requests with a Jenkinsfile.')
    project.save()
    println("Created the ${projectName} Multibranch Pipeline.")
} else {
    println("${projectName} Multibranch Pipeline already exists; leaving its settings unchanged.")
}

if (createdProject) {
    project.scheduleBuild2(0)
    println("Queued the initial ${projectName} Multibranch Pipeline scan.")
}
