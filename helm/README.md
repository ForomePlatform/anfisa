### Installation instructions

- To install Anfisa on a OpenShift cluster:

1. Login to your OpenShift Cluster

2. #### Go to your project

`oc project PROJECT_NAME`

3. #### Clone repository

`git clone -b v.0.7 https://github.com/ForomePlatform/anfisa-openshift.git`

4. `cd anfisa-openshift/anfisa-chart`

5. Edit values.yml

6. #### Assign the anyuid security context constraint to the project
`oc adm policy add-scc-to-user anyuid system:serviceaccount:<project name>:default`

7. #### Grant all authenticated users access to the anyuid SCC
`oc adm policy add-scc-to-group anyuid system:authenticated`

8. #### Add the IBM Cloud Helm repository ibm-helm to your cluster
`helm repo add ibm-helm https://raw.githubusercontent.com/IBM/charts/master/repo/ibm-helm`

9. #### Update the Helm repo to retrieve the latest version of all Helm charts in this repo.
`helm repo update`

10. #### Download the Helm chart and unpack the chart in your current directory. Then, navigate to the ibm-object-storage-plugin directory
`helm fetch --untar ibm-helm/ibm-object-storage-plugin && cd ibm-object-storage-plugin`

11. #### Install the ibmc Helm plug-in
`helm plugin install ./helm-ibmc`

12. #### Verify that the ibmc plug-in is installed successfully
`helm ibmc --help`

13. #### Install the IBM Cloud Object Storage plug-in. When you install the plug-in, pre-defined storage classes are added to your cluster
`helm ibmc install ibm-object-storage-plugin ibm-helm/ibm-object-storage-plugin --set license=true`

14. #### Verify that the storage classes are created successfully. Note that this output varies depending on the type of cluster you use.
`oc get storageclass | grep 'ibmc-s3fs`

16. #### Install anfisa via Helm
`helm upgrade --install anfisa -n PROJECT_NAME --debug .`

17. #### In openshift console start all builds
`click BUILD -> buildconfigs -> start build`
or
`oc start-build <build-name> --follow`
